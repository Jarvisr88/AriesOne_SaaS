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
  Headers,
  Res,
} from '@nestjs/common';
import { Response } from 'express';
import { AuthGuard } from '@nestjs/passport';
import { ReportService } from '../services/report.service';
import {
  SearchReportsDto,
  CreateReportDto,
  UpdateReportDto,
} from '../dto/report.dto';
import { CurrentUser } from '../decorators/current-user.decorator';
import { User } from '../interfaces/user.interface';

@Controller('api/reports')
@UseGuards(AuthGuard('jwt'))
export class ReportController {
  constructor(private readonly reportService: ReportService) {}

  @Get()
  async searchReports(@Query() searchDto: SearchReportsDto) {
    return this.reportService.searchReports(searchDto);
  }

  @Get(':id')
  async getReport(@Param('id') id: string) {
    return this.reportService.getReportById(id);
  }

  @Post()
  async createReport(
    @Body() createDto: CreateReportDto,
    @CurrentUser() user: User,
  ) {
    return this.reportService.createReport(createDto, user.id);
  }

  @Put(':id')
  async updateReport(
    @Param('id') id: string,
    @Body() updateDto: UpdateReportDto,
    @CurrentUser() user: User,
  ) {
    return this.reportService.updateReport(id, updateDto, user.id);
  }

  @Delete()
  async deleteReports(
    @Body('ids') ids: string[],
    @CurrentUser() user: User,
  ) {
    return this.reportService.deleteReports(ids, user.id);
  }

  @Post(':id/clone')
  async cloneReport(
    @Param('id') id: string,
    @Body('name') newName: string,
    @CurrentUser() user: User,
  ) {
    return this.reportService.cloneReport(id, newName, user.id);
  }

  @Get(':id/export')
  async exportReport(
    @Param('id') id: string,
    @Query('format') format: string,
    @CurrentUser() user: User,
    @Headers('user-agent') userAgent: string,
    @Res() res: Response,
  ) {
    const buffer = await this.reportService.exportReport(id, format, user.id);
    
    const report = await this.reportService.getReportById(id);
    const filename = `${report.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${format}`;
    
    res.set({
      'Content-Type': this.getContentType(format),
      'Content-Disposition': `attachment; filename="${filename}"`,
      'Content-Length': buffer.length,
    });

    res.end(buffer);
  }

  @Get(':id/audit')
  async getReportAuditHistory(
    @Param('id') id: string,
    @Query('offset') offset: number,
    @Query('limit') limit: number,
  ) {
    return this.reportService.getReportAuditHistory(id, offset, limit);
  }

  private getContentType(format: string): string {
    switch (format.toLowerCase()) {
      case 'pdf':
        return 'application/pdf';
      case 'excel':
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      case 'csv':
        return 'text/csv';
      default:
        return 'application/octet-stream';
    }
  }
}
