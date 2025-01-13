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
import { ClientService } from '../services/client.service';
import { JwtAuthGuard } from '../guards/jwt-auth.guard';
import { RolesGuard } from '../guards/roles.guard';
import { Roles } from '../decorators/roles.decorator';
import { CurrentUser } from '../decorators/current-user.decorator';
import {
  CreateClientDto,
  UpdateClientDto,
  ClientResponseDto,
} from '../dto/client.dto';
import { PaginationDto } from '../dto/common.dto';

@ApiTags('clients')
@Controller('clients')
@UseGuards(JwtAuthGuard, RolesGuard)
export class ClientController {
  constructor(private readonly clientService: ClientService) {}

  @Post()
  @Roles('admin')
  @ApiOperation({ summary: 'Create a new client' })
  @ApiResponse({ status: HttpStatus.CREATED, type: ClientResponseDto })
  async create(
    @Body() dto: CreateClientDto,
    @CurrentUser('id') userId: string,
  ) {
    return this.clientService.create(dto, userId);
  }

  @Get()
  @Roles('admin', 'user')
  @ApiOperation({ summary: 'Get all clients' })
  @ApiResponse({ status: HttpStatus.OK, type: [ClientResponseDto] })
  async findAll(@Query() pagination: PaginationDto) {
    const [clients, total] = await this.clientService.findAll(pagination);
    return {
      data: clients,
      total,
      ...pagination,
    };
  }

  @Get(':id')
  @Roles('admin', 'user')
  @ApiOperation({ summary: 'Get a client by id' })
  @ApiResponse({ status: HttpStatus.OK, type: ClientResponseDto })
  async findOne(@Param('id', ParseUUIDPipe) id: string) {
    return this.clientService.findOne(id);
  }

  @Put(':id')
  @Roles('admin')
  @ApiOperation({ summary: 'Update a client' })
  @ApiResponse({ status: HttpStatus.OK, type: ClientResponseDto })
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() dto: UpdateClientDto,
    @CurrentUser('id') userId: string,
  ) {
    return this.clientService.update(id, dto, userId);
  }

  @Delete(':id')
  @Roles('admin')
  @ApiOperation({ summary: 'Delete a client' })
  @ApiResponse({ status: HttpStatus.NO_CONTENT })
  async delete(
    @Param('id', ParseUUIDPipe) id: string,
    @CurrentUser('id') userId: string,
  ) {
    await this.clientService.delete(id, userId);
  }

  @Get(':id/stats')
  @Roles('admin', 'user')
  @ApiOperation({ summary: 'Get client serial statistics' })
  @ApiResponse({ status: HttpStatus.OK })
  async getStats(@Param('id', ParseUUIDPipe) id: string) {
    return this.clientService.getSerialStats(id);
  }

  @Get('search')
  @Roles('admin', 'user')
  @ApiOperation({ summary: 'Search clients' })
  @ApiResponse({ status: HttpStatus.OK, type: [ClientResponseDto] })
  async search(
    @Query('query') query: string,
    @Query() pagination: PaginationDto,
  ) {
    const [clients, total] = await this.clientService.search(query, pagination);
    return {
      data: clients,
      total,
      ...pagination,
    };
  }
}
