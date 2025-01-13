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
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { TemplateService } from '../services/template.service';
import {
  CreateTemplateDto,
  UpdateTemplateDto,
} from '../dto/template.dto';
import { CurrentUser } from '../decorators/current-user.decorator';
import { User } from '../interfaces/user.interface';

@Controller('api/report-templates')
@UseGuards(AuthGuard('jwt'))
export class TemplateController {
  constructor(private readonly templateService: TemplateService) {}

  @Get()
  async getTemplates(
    @Query('type') type: string,
    @Query('offset') offset: number,
    @Query('limit') limit: number,
  ) {
    return this.templateService.getTemplates(type, offset, limit);
  }

  @Get(':id')
  async getTemplate(@Param('id') id: string) {
    return this.templateService.getTemplateById(id);
  }

  @Post()
  async createTemplate(
    @Body() createDto: CreateTemplateDto,
    @CurrentUser() user: User,
  ) {
    return this.templateService.createTemplate(createDto, user.id);
  }

  @Put(':id')
  async updateTemplate(
    @Param('id') id: string,
    @Body() updateDto: UpdateTemplateDto,
    @CurrentUser() user: User,
  ) {
    return this.templateService.updateTemplate(id, updateDto, user.id);
  }

  @Delete(':id')
  async deleteTemplate(@Param('id') id: string) {
    return this.templateService.deleteTemplate(id);
  }

  @Post('validate')
  async validateTemplate(@Body() templateData: any) {
    return this.templateService.validateTemplate(templateData);
  }
}
