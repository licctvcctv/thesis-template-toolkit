package com.heath.community.controller;

import com.heath.community.common.PageResult;
import com.heath.community.common.Result;
import com.heath.community.dto.FollowupRecordDTO;
import com.heath.community.entity.FollowupRecord;
import com.heath.community.service.FollowupRecordService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;

@RestController
@RequestMapping("/api/followup-record")
@RequiredArgsConstructor
public class FollowupRecordController {
    private final FollowupRecordService followupRecordService;

    @GetMapping("/page")
    public Result<PageResult<FollowupRecordDTO>> findPage(
            @RequestParam(required = false) Long patientId,
            @RequestParam(required = false) Long doctorId,
            @RequestParam(required = false) Long taskId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size) {
        return Result.success(followupRecordService.findPage(patientId, doctorId, taskId, startDate, endDate, page, size));
    }

    @GetMapping("/{id}")
    public Result<FollowupRecordDTO> findById(@PathVariable Long id) {
        return Result.success(followupRecordService.findById(id));
    }

    @PostMapping
    public Result<Void> create(@RequestBody FollowupRecord record) {
        followupRecordService.create(record);
        return Result.success();
    }

    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody FollowupRecord record) {
        record.setId(id);
        followupRecordService.update(record);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        followupRecordService.delete(id);
        return Result.success();
    }

    @GetMapping("/{id}/export")
    public Result<String> export(@PathVariable Long id) {
        FollowupRecordDTO record = followupRecordService.findById(id);
        if (record == null) {
            return Result.error("随访记录不存在");
        }
        String html = generateHtmlReport(record);
        return Result.success(html);
    }

    private String generateHtmlReport(FollowupRecordDTO record) {
        StringBuilder html = new StringBuilder();
        html.append("<!DOCTYPE html>\n");
        html.append("<html>\n");
        html.append("<head>\n");
        html.append("<meta charset=\"UTF-8\">\n");
        html.append("<title>随访记录报告单</title>\n");
        html.append("<style>\n");
        html.append("body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }\n");
        html.append(".container { background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto; }\n");
        html.append("h1 { text-align: center; color: #409eff; border-bottom: 3px solid #409eff; padding-bottom: 10px; }\n");
        html.append(".info-section { margin: 20px 0; }\n");
        html.append(".info-row { display: flex; margin: 10px 0; padding: 8px; background-color: #f9f9f9; border-left: 3px solid #409eff; }\n");
        html.append(".info-label { font-weight: bold; width: 120px; color: #606266; }\n");
        html.append(".info-value { flex: 1; color: #303133; }\n");
        html.append(".section-title { font-size: 18px; font-weight: bold; color: #409eff; margin: 20px 0 10px 0; padding-bottom: 5px; border-bottom: 2px solid #e4e7ed; }\n");
        html.append(".content-box { padding: 15px; background-color: #fafafa; border-radius: 4px; margin: 10px 0; line-height: 1.6; color: #303133; }\n");
        html.append(".footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e4e7ed; color: #909399; font-size: 12px; }\n");
        html.append("</style>\n");
        html.append("</head>\n");
        html.append("<body>\n");
        html.append("<div class=\"container\">\n");
        html.append("<h1>随访记录报告单</h1>\n");

        html.append("<div class=\"info-section\">\n");
        html.append("<div class=\"section-title\">基本信息</div>\n");
        html.append("<div class=\"info-row\"><span class=\"info-label\">患者姓名：</span><span class=\"info-value\">").append(record.getPatientName() != null ? record.getPatientName() : "").append("</span></div>\n");
        html.append("<div class=\"info-row\"><span class=\"info-label\">随访医生：</span><span class=\"info-value\">").append(record.getDoctorName() != null ? record.getDoctorName() : "").append("</span></div>\n");
        html.append("<div class=\"info-row\"><span class=\"info-label\">随访日期：</span><span class=\"info-value\">").append(record.getFollowupDate() != null ? record.getFollowupDate().toString() : "").append("</span></div>\n");
        html.append("<div class=\"info-row\"><span class=\"info-label\">随访类型：</span><span class=\"info-value\">").append(record.getFollowupType() != null ? record.getFollowupType() : "").append("</span></div>\n");
        if (record.getTaskNo() != null) {
            html.append("<div class=\"info-row\"><span class=\"info-label\">任务编号：</span><span class=\"info-value\">").append(record.getTaskNo()).append("</span></div>\n");
        }
        html.append("</div>\n");

        html.append("<div class=\"info-section\">\n");
        html.append("<div class=\"section-title\">症状描述</div>\n");
        html.append("<div class=\"content-box\">").append(record.getSymptoms() != null ? record.getSymptoms().replace("\n", "<br>") : "无").append("</div>\n");
        html.append("</div>\n");

        html.append("<div class=\"info-section\">\n");
        html.append("<div class=\"section-title\">检查指标</div>\n");
        html.append("<div class=\"info-row\"><span class=\"info-label\">血压：</span><span class=\"info-value\">").append(record.getBloodPressure() != null ? record.getBloodPressure() : "未测量").append("</span></div>\n");
        html.append("<div class=\"info-row\"><span class=\"info-label\">血糖：</span><span class=\"info-value\">").append(record.getBloodSugar() != null ? record.getBloodSugar() : "未测量").append("</span></div>\n");
        html.append("<div class=\"info-row\"><span class=\"info-label\">体重：</span><span class=\"info-value\">").append(record.getWeight() != null ? record.getWeight() + " kg" : "未测量").append("</span></div>\n");
        html.append("</div>\n");

        html.append("<div class=\"info-section\">\n");
        html.append("<div class=\"section-title\">用药明细</div>\n");
        if (record.getMedicines() != null && !record.getMedicines().isEmpty()) {
            html.append("<table style=\"width: 100%; border-collapse: collapse; margin: 10px 0;\">\n");
            html.append("<thead>\n");
            html.append("<tr style=\"background-color: #f5f7fa;\">\n");
            html.append("<th style=\"padding: 10px; text-align: left; border: 1px solid #e4e7ed;\">药品名称</th>\n");
            html.append("<th style=\"padding: 10px; text-align: center; border: 1px solid #e4e7ed; width: 100px;\">数量</th>\n");
            html.append("<th style=\"padding: 10px; text-align: left; border: 1px solid #e4e7ed;\">用法用量</th>\n");
            html.append("</tr>\n");
            html.append("</thead>\n");
            html.append("<tbody>\n");
            for (com.heath.community.dto.FollowupRecordMedicineDTO medicine : record.getMedicines()) {
                html.append("<tr>\n");
                html.append("<td style=\"padding: 10px; border: 1px solid #e4e7ed;\">");
                html.append(medicine.getMedicineName() != null ? medicine.getMedicineName() : "");
                if (medicine.getMedicineCode() != null && !medicine.getMedicineCode().isEmpty()) {
                    html.append(" (").append(medicine.getMedicineCode()).append(")");
                }
                html.append("</td>\n");
                html.append("<td style=\"padding: 10px; text-align: center; border: 1px solid #e4e7ed;\">");
                html.append(medicine.getQuantity() != null ? medicine.getQuantity().toString() : "");
                html.append("</td>\n");
                html.append("<td style=\"padding: 10px; border: 1px solid #e4e7ed;\">");
                html.append(medicine.getDosage() != null ? medicine.getDosage() : "");
                html.append("</td>\n");
                html.append("</tr>\n");
            }
            html.append("</tbody>\n");
            html.append("</table>\n");
        } else {
            html.append("<div class=\"content-box\">无</div>\n");
        }
        html.append("</div>\n");

        html.append("<div class=\"info-section\">\n");
        html.append("<div class=\"section-title\">用药依从性</div>\n");
        html.append("<div class=\"content-box\">").append(record.getMedicationCompliance() != null ? record.getMedicationCompliance().replace("\n", "<br>") : "无").append("</div>\n");
        html.append("</div>\n");

        if (record.getAdverseReactions() != null && !record.getAdverseReactions().isEmpty()) {
            html.append("<div class=\"info-section\">\n");
            html.append("<div class=\"section-title\">不良反应</div>\n");
            html.append("<div class=\"content-box\">").append(record.getAdverseReactions().replace("\n", "<br>")).append("</div>\n");
            html.append("</div>\n");
        }

        html.append("<div class=\"info-section\">\n");
        html.append("<div class=\"section-title\">生活方式指导</div>\n");
        html.append("<div class=\"content-box\">").append(record.getLifestyleGuidance() != null ? record.getLifestyleGuidance().replace("\n", "<br>") : "无").append("</div>\n");
        html.append("</div>\n");

        html.append("<div class=\"info-section\">\n");
        html.append("<div class=\"section-title\">随访结果</div>\n");
        html.append("<div class=\"content-box\">").append(record.getFollowupResult() != null ? record.getFollowupResult().replace("\n", "<br>") : "无").append("</div>\n");
        html.append("</div>\n");

        if (record.getNextFollowupDate() != null) {
            html.append("<div class=\"info-section\">\n");
            html.append("<div class=\"section-title\">下次随访</div>\n");
            html.append("<div class=\"info-row\"><span class=\"info-label\">下次随访日期：</span><span class=\"info-value\">").append(record.getNextFollowupDate().toString()).append("</span></div>\n");
            html.append("</div>\n");
        }

        if (record.getRemarks() != null && !record.getRemarks().isEmpty()) {
            html.append("<div class=\"info-section\">\n");
            html.append("<div class=\"section-title\">备注</div>\n");
            html.append("<div class=\"content-box\">").append(record.getRemarks().replace("\n", "<br>")).append("</div>\n");
            html.append("</div>\n");
        }

        html.append("<div class=\"footer\">\n");
        html.append("<p>报告生成时间：").append(java.time.LocalDateTime.now().toString()).append("</p>\n");
        html.append("</div>\n");

        html.append("</div>\n");
        html.append("</body>\n");
        html.append("</html>\n");
        return html.toString();
    }
}
