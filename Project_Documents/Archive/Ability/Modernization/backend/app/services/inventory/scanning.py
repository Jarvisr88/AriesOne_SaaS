from datetime import datetime
from typing import List, Dict, Optional, Union
import cv2
import numpy as np
from pyzbar.pyzbar import decode as pyzbar_decode
from pyzbar.pyzbar import ZBarSymbol
import mercury
from fastapi import HTTPException, UploadFile
import asyncio
from PIL import Image
import io

from app.models.inventory import (
    InventoryItem,
    ScannedItem,
    RFIDTag,
    SerialNumber,
    BatchScan
)
from app.core.config import Settings
from app.core.logging import logger
from app.services.storage import StorageService

class ScanningService:
    def __init__(
        self,
        settings: Settings,
        storage_service: StorageService
    ):
        self.settings = settings
        self.storage_service = storage_service
        self.rfid_reader = mercury.Reader(settings.rfid.reader_url)
        self.supported_barcode_formats = [
            ZBarSymbol.EAN13,
            ZBarSymbol.EAN8,
            ZBarSymbol.CODE128,
            ZBarSymbol.CODE39,
            ZBarSymbol.QRCODE,
            ZBarSymbol.DATAMATRIX
        ]

    async def scan_barcode(
        self,
        image: Union[UploadFile, bytes],
        scan_type: str = 'all'
    ) -> List[Dict]:
        """
        Scan barcode from image
        """
        try:
            # Convert image to numpy array
            if isinstance(image, UploadFile):
                contents = await image.read()
                nparr = np.frombuffer(contents, np.uint8)
            else:
                nparr = np.frombuffer(image, np.uint8)

            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

            # Enhance image for better scanning
            img = cv2.adaptiveThreshold(
                img,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )

            # Scan for barcodes
            formats = (
                [ZBarSymbol[scan_type.upper()]]
                if scan_type != 'all'
                else self.supported_barcode_formats
            )

            decoded_objects = pyzbar_decode(img, symbols=formats)
            
            results = []
            for obj in decoded_objects:
                result = {
                    'type': obj.type,
                    'data': obj.data.decode('utf-8'),
                    'rect': {
                        'left': obj.rect.left,
                        'top': obj.rect.top,
                        'width': obj.rect.width,
                        'height': obj.rect.height
                    },
                    'polygon': [
                        {'x': point.x, 'y': point.y}
                        for point in obj.polygon
                    ]
                }
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error scanning barcode: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error scanning barcode: {str(e)}"
            )

    async def scan_rfid(
        self,
        antenna_port: int = 1,
        power_level: int = 23,
        timeout: int = 1000
    ) -> List[Dict]:
        """
        Scan RFID tags using Mercury reader
        """
        try:
            self.rfid_reader.set_region('NA')
            self.rfid_reader.set_read_plan(
                [antenna_port],
                'GEN2',
                read_power=power_level
            )

            tags = self.rfid_reader.read(timeout)
            
            results = []
            for tag in tags:
                result = {
                    'epc': tag.epc.hex(),
                    'antenna': tag.antenna,
                    'read_count': tag.read_count,
                    'rssi': tag.rssi
                }
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error scanning RFID: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error scanning RFID: {str(e)}"
            )

    async def process_batch_scan(
        self,
        images: List[UploadFile],
        scan_type: str = 'all'
    ) -> BatchScan:
        """
        Process multiple scans in batch
        """
        try:
            batch = await BatchScan.create(
                started_at=datetime.now(),
                status='processing'
            )

            results = []
            errors = []

            for image in images:
                try:
                    scan_results = await self.scan_barcode(image, scan_type)
                    results.extend(scan_results)
                except Exception as e:
                    errors.append({
                        'filename': image.filename,
                        'error': str(e)
                    })

            batch.completed_at = datetime.now()
            batch.status = 'completed'
            batch.total_scans = len(results)
            batch.error_count = len(errors)
            await batch.save()

            return batch

        except Exception as e:
            logger.error(f"Error processing batch scan: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing batch scan: {str(e)}"
            )

    async def track_serial_number(
        self,
        item_id: str,
        serial_number: str,
        expiration_date: Optional[datetime] = None
    ) -> SerialNumber:
        """
        Track item serial number
        """
        try:
            item = await InventoryItem.get_or_none(id=item_id)
            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found"
                )

            serial = await SerialNumber.create(
                item=item,
                serial_number=serial_number,
                expiration_date=expiration_date,
                status='active',
                created_at=datetime.now()
            )

            return serial

        except Exception as e:
            logger.error(f"Error tracking serial number: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error tracking serial number: {str(e)}"
            )

    async def link_rfid_tag(
        self,
        item_id: str,
        epc: str,
        metadata: Optional[Dict] = None
    ) -> RFIDTag:
        """
        Link RFID tag to inventory item
        """
        try:
            item = await InventoryItem.get_or_none(id=item_id)
            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found"
                )

            tag = await RFIDTag.create(
                item=item,
                epc=epc,
                metadata=metadata,
                status='active',
                created_at=datetime.now()
            )

            return tag

        except Exception as e:
            logger.error(f"Error linking RFID tag: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error linking RFID tag: {str(e)}"
            )

    async def process_offline_scans(
        self,
        offline_data: List[Dict]
    ) -> Dict:
        """
        Process scans captured offline
        """
        try:
            results = {
                'processed': 0,
                'errors': 0,
                'details': []
            }

            for scan in offline_data:
                try:
                    if scan['type'] == 'barcode':
                        image_data = base64.b64decode(scan['image'])
                        scan_results = await self.scan_barcode(image_data)
                    elif scan['type'] == 'rfid':
                        scan_results = [{
                            'epc': scan['epc'],
                            'timestamp': scan['timestamp']
                        }]
                    
                    await ScannedItem.create(
                        scan_type=scan['type'],
                        scan_data=scan_results,
                        scanned_at=datetime.fromisoformat(scan['timestamp']),
                        location=scan.get('location'),
                        device_id=scan.get('device_id')
                    )
                    
                    results['processed'] += 1
                    results['details'].append({
                        'status': 'success',
                        'timestamp': scan['timestamp'],
                        'results': scan_results
                    })
                
                except Exception as e:
                    results['errors'] += 1
                    results['details'].append({
                        'status': 'error',
                        'timestamp': scan['timestamp'],
                        'error': str(e)
                    })

            return results

        except Exception as e:
            logger.error(f"Error processing offline scans: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing offline scans: {str(e)}"
            )
