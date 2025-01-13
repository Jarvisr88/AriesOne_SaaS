import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  UseGuards,
  HttpStatus,
  ParseUUIDPipe,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { SerialService } from '../services/serial.service';
import { JwtAuthGuard } from '../guards/jwt-auth.guard';
import { RolesGuard } from '../guards/roles.guard';
import { Roles } from '../decorators/roles.decorator';
import { CurrentUser } from '../decorators/current-user.decorator';
import {
  CreateSerialDto,
  UpdateSerialDto,
  ValidateSerialDto,
  SerialResponseDto,
} from '../dto/serial.dto';
import { PaginationDto } from '../dto/common.dto';

@ApiTags('serials')
@Controller('serials')
@UseGuards(JwtAuthGuard, RolesGuard)
export class SerialController {
  constructor(private readonly serialService: SerialService) {}

  @Post()
  @Roles('admin')
  @ApiOperation({ summary: 'Create a new serial' })
  @ApiResponse({ status: HttpStatus.CREATED, type: SerialResponseDto })
  async create(
    @Body() dto: CreateSerialDto,
    @CurrentUser('id') userId: string,
  ) {
    return this.serialService.create(dto, userId);
  }

  @Post('bulk')
  @Roles('admin')
  @ApiOperation({ summary: 'Create multiple serials' })
  @ApiResponse({ status: HttpStatus.CREATED, type: [SerialResponseDto] })
  async createBulk(
    @Body() dtos: CreateSerialDto[],
    @CurrentUser('id') userId: string,
  ) {
    return this.serialService.createBulk(dtos, userId);
  }

  @Get()
  @Roles('admin', 'user')
  @ApiOperation({ summary: 'Get all serials' })
  @ApiResponse({ status: HttpStatus.OK, type: [SerialResponseDto] })
  async findAll(@Query() pagination: PaginationDto) {
    const [serials, total] = await this.serialService.findAll(pagination);
    return {
      data: serials,
      total,
      ...pagination,
    };
  }

  @Get(':id')
  @Roles('admin', 'user')
  @ApiOperation({ summary: 'Get a serial by id' })
  @ApiResponse({ status: HttpStatus.OK, type: SerialResponseDto })
  async findOne(@Param('id', ParseUUIDPipe) id: string) {
    return this.serialService.findOne(id);
  }

  @Put(':id')
  @Roles('admin')
  @ApiOperation({ summary: 'Update a serial' })
  @ApiResponse({ status: HttpStatus.OK, type: SerialResponseDto })
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() dto: UpdateSerialDto,
    @CurrentUser('id') userId: string,
  ) {
    return this.serialService.update(id, dto, userId);
  }

  @Delete(':id')
  @Roles('admin')
  @ApiOperation({ summary: 'Delete a serial' })
  @ApiResponse({ status: HttpStatus.NO_CONTENT })
  async delete(
    @Param('id', ParseUUIDPipe) id: string,
    @CurrentUser('id') userId: string,
  ) {
    await this.serialService.delete(id, userId);
  }

  @Post('validate')
  @ApiOperation({ summary: 'Validate a serial' })
  @ApiResponse({ status: HttpStatus.OK, type: Boolean })
  async validate(@Body() dto: ValidateSerialDto) {
    return this.serialService.validate(dto);
  }

  @Post(':id/revoke')
  @Roles('admin')
  @ApiOperation({ summary: 'Revoke a serial' })
  @ApiResponse({ status: HttpStatus.OK })
  async revoke(
    @Param('id', ParseUUIDPipe) id: string,
    @CurrentUser('id') userId: string,
  ) {
    await this.serialService.revoke(id, userId);
  }

  @Post(':id/renew')
  @Roles('admin')
  @ApiOperation({ summary: 'Renew a serial' })
  @ApiResponse({ status: HttpStatus.OK, type: SerialResponseDto })
  async renew(
    @Param('id', ParseUUIDPipe) id: string,
    @Body('expirationDate') expirationDate: Date,
    @CurrentUser('id') userId: string,
  ) {
    return this.serialService.renew(id, expirationDate, userId);
  }

  @Get(':id/stats')
  @Roles('admin', 'user')
  @ApiOperation({ summary: 'Get serial usage statistics' })
  @ApiResponse({ status: HttpStatus.OK })
  async getStats(@Param('id', ParseUUIDPipe) id: string) {
    return this.serialService.getUsageStats(id);
  }
}
