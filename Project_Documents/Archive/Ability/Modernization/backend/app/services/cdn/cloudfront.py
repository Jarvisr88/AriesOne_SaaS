from typing import Optional, Dict, List
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import aioboto3
from app.services.cdn.base import (
    BaseCDN,
    CDNProvider,
    CDNRegion,
    OptimizationType,
    CDNException,
    CDNUploadError,
    CDNInvalidationError,
    CDNOptimizationError
)
from app.core.config import settings
from app.core.logging import logger

class CloudFrontCDN(BaseCDN):
    def __init__(
        self,
        region: CDNRegion,
        config: Dict
    ):
        super().__init__(CDNProvider.CLOUDFRONT, region, config)
        
        self.distribution_id = config["distribution_id"]
        self.bucket_name = config["bucket_name"]
        self.key_pair_id = config["key_pair_id"]
        self.private_key = config["private_key"]
        
        # Configure AWS clients
        aws_config = Config(
            region_name=region,
            retries=dict(max_attempts=3)
        )
        
        self.cloudfront_client = boto3.client(
            'cloudfront',
            config=aws_config,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        self.s3_session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

    async def health_check(self) -> bool:
        """Check CloudFront health"""
        try:
            response = self.cloudfront_client.get_distribution(
                Id=self.distribution_id
            )
            status = response['Distribution']['Status']
            return status == 'Deployed'
        except Exception as e:
            logger.error(f"CloudFront health check error: {e}")
            return False

    async def upload_file(
        self,
        file_path: str,
        content: bytes,
        content_type: str
    ) -> str:
        """Upload file to S3 and return CloudFront URL"""
        try:
            async with self.s3_session.client('s3') as s3:
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=file_path,
                    Body=content,
                    ContentType=content_type,
                    CacheControl='max-age=31536000'  # 1 year
                )
            
            return await self.get_url(file_path)
        except Exception as e:
            logger.error(f"CloudFront upload error: {e}")
            raise CDNUploadError(f"Failed to upload file: {e}")

    async def get_url(
        self,
        file_path: str,
        ttl: Optional[int] = None
    ) -> str:
        """Get signed CloudFront URL"""
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            import rsa
            
            # Parse private key
            private_key = serialization.load_pem_private_key(
                self.private_key.encode('utf-8'),
                password=None
            )
            
            # Create CloudFront signer
            from botocore.signers import CloudFrontSigner
            
            def rsa_signer(message):
                return private_key.sign(
                    message,
                    padding.PKCS1v15(),
                    rsa.SHA1()
                )
            
            # Create signed URL
            url = f"https://{self.config['domain']}/{file_path}"
            
            if ttl:
                expire_date = (datetime.utcnow() + 
                             timedelta(seconds=ttl)).strftime(
                    '%Y-%m-%dT%H:%M:%SZ'
                )
            else:
                expire_date = (datetime.utcnow() + 
                             timedelta(days=7)).strftime(
                    '%Y-%m-%dT%H:%M:%SZ'
                )
            
            cloudfront_signer = CloudFrontSigner(
                self.key_pair_id,
                rsa_signer
            )
            
            signed_url = cloudfront_signer.generate_presigned_url(
                url,
                date_less_than=expire_date
            )
            
            return signed_url
        except Exception as e:
            logger.error(f"CloudFront URL signing error: {e}")
            raise CDNException(f"Failed to generate signed URL: {e}")

    async def invalidate(self, paths: List[str]) -> None:
        """Invalidate CloudFront cache"""
        try:
            self.cloudfront_client.create_invalidation(
                DistributionId=self.distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': str(datetime.utcnow().timestamp())
                }
            )
        except Exception as e:
            logger.error(f"CloudFront invalidation error: {e}")
            raise CDNInvalidationError(f"Failed to invalidate paths: {e}")

    async def optimize(
        self,
        file_path: str,
        optimization_type: OptimizationType
    ) -> str:
        """Optimize file using Lambda@Edge"""
        try:
            # Add optimization parameters to URL
            params = {
                OptimizationType.IMAGE: {
                    'auto': 'compress,format',
                    'q': '80'
                },
                OptimizationType.VIDEO: {
                    'auto': 'compress',
                    'br': '2000'
                },
                OptimizationType.JS: {
                    'auto': 'minify'
                },
                OptimizationType.CSS: {
                    'auto': 'minify'
                },
                OptimizationType.HTML: {
                    'auto': 'minify'
                }
            }
            
            url = await self.get_url(file_path)
            if optimization_type in params:
                url_params = '&'.join(
                    f"{k}={v}" for k, v in params[optimization_type].items()
                )
                url = f"{url}?{url_params}"
            
            return url
        except Exception as e:
            logger.error(f"CloudFront optimization error: {e}")
            raise CDNOptimizationError(f"Failed to optimize file: {e}")
