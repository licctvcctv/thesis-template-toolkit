package com.heath.community.util;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.web.multipart.MultipartFile;

import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class ExcelUtil {

    public static void exportPatient(List<PatientExportData> dataList, HttpServletResponse response) throws IOException {
        Workbook workbook = new XSSFWorkbook();
        Sheet sheet = workbook.createSheet("患者信息");

        CellStyle headerStyle = workbook.createCellStyle();
        Font headerFont = workbook.createFont();
        headerFont.setBold(true);
        headerFont.setFontHeightInPoints((short) 12);
        headerStyle.setFont(headerFont);
        headerStyle.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.getIndex());
        headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        headerStyle.setAlignment(HorizontalAlignment.CENTER);
        headerStyle.setVerticalAlignment(VerticalAlignment.CENTER);

        CellStyle dataStyle = workbook.createCellStyle();
        dataStyle.setAlignment(HorizontalAlignment.LEFT);
        dataStyle.setVerticalAlignment(VerticalAlignment.CENTER);

        Row headerRow = sheet.createRow(0);
        String[] headers = {"患者编号", "姓名", "性别", "出生日期", "身份证号", "手机号", "地址", "疾病类型", "确诊日期", "风险等级", "负责医生"};
        for (int i = 0; i < headers.length; i++) {
            Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
            cell.setCellStyle(headerStyle);
        }

        int rowNum = 1;
        for (PatientExportData data : dataList) {
            Row row = sheet.createRow(rowNum++);
            int colNum = 0;

            row.createCell(colNum++).setCellValue(data.getPatientNo() != null ? data.getPatientNo() : "");
            row.createCell(colNum++).setCellValue(data.getName() != null ? data.getName() : "");
            row.createCell(colNum++).setCellValue(data.getGender() != null ? (data.getGender() == 1 ? "男" : data.getGender() == 2 ? "女" : "") : "");
            row.createCell(colNum++).setCellValue(data.getBirthday() != null ? data.getBirthday().format(DateTimeFormatter.ofPattern("yyyy-MM-dd")) : "");
            row.createCell(colNum++).setCellValue(data.getIdCard() != null ? data.getIdCard() : "");
            row.createCell(colNum++).setCellValue(data.getPhone() != null ? data.getPhone() : "");
            row.createCell(colNum++).setCellValue(data.getAddress() != null ? data.getAddress() : "");
            row.createCell(colNum++).setCellValue(data.getDiseaseType() != null ? data.getDiseaseType() : "");
            row.createCell(colNum++).setCellValue(data.getDiagnosisDate() != null ? data.getDiagnosisDate().format(DateTimeFormatter.ofPattern("yyyy-MM-dd")) : "");
            row.createCell(colNum++).setCellValue(data.getRiskLevelName() != null ? data.getRiskLevelName() : "");
            row.createCell(colNum++).setCellValue(data.getDoctorName() != null ? data.getDoctorName() : "");

            for (int i = 0; i < colNum; i++) {
                row.getCell(i).setCellStyle(dataStyle);
            }
        }

        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
            sheet.setColumnWidth(i, sheet.getColumnWidth(i) + 2000);
        }

        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        String fileName = URLEncoder.encode("患者信息_" + LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd")), StandardCharsets.UTF_8);
        response.setHeader("Content-Disposition", "attachment; filename=" + fileName + ".xlsx");

        try (OutputStream outputStream = response.getOutputStream()) {
            workbook.write(outputStream);
        } finally {
            workbook.close();
        }
    }

    public static List<PatientImportData> importPatient(MultipartFile file) throws IOException {
        List<PatientImportData> dataList = new ArrayList<>();
        
        try (InputStream inputStream = file.getInputStream();
             Workbook workbook = WorkbookFactory.create(inputStream)) {
            
            Sheet sheet = workbook.getSheetAt(0);
            
            for (int i = 1; i <= sheet.getLastRowNum(); i++) {
                Row row = sheet.getRow(i);
                if (row == null) {
                    continue;
                }
                
                PatientImportData data = new PatientImportData();
                int colNum = 0;
                
                if (getCellValue(row.getCell(colNum++)) != null && !getCellValue(row.getCell(colNum - 1)).isEmpty()) {
                    data.setPatientNo(getCellValue(row.getCell(colNum - 1)));
                }
                data.setName(getCellValue(row.getCell(colNum++)));
                
                String genderStr = getCellValue(row.getCell(colNum++));
                if ("男".equals(genderStr)) {
                    data.setGender(1);
                } else if ("女".equals(genderStr)) {
                    data.setGender(2);
                }
                
                String birthdayStr = getCellValue(row.getCell(colNum++));
                if (birthdayStr != null && !birthdayStr.isEmpty()) {
                    try {
                        data.setBirthday(LocalDate.parse(birthdayStr, DateTimeFormatter.ofPattern("yyyy-MM-dd")));
                    } catch (Exception e) {
                        // 忽略日期解析错误
                    }
                }
                
                data.setIdCard(getCellValue(row.getCell(colNum++)));
                data.setPhone(getCellValue(row.getCell(colNum++)));
                data.setAddress(getCellValue(row.getCell(colNum++)));
                data.setDiseaseType(getCellValue(row.getCell(colNum++)));
                
                String diagnosisDateStr = getCellValue(row.getCell(colNum++));
                if (diagnosisDateStr != null && !diagnosisDateStr.isEmpty()) {
                    try {
                        data.setDiagnosisDate(LocalDate.parse(diagnosisDateStr, DateTimeFormatter.ofPattern("yyyy-MM-dd")));
                    } catch (Exception e) {
                        // 忽略日期解析错误
                    }
                }
                
                String riskLevelName = getCellValue(row.getCell(colNum++));
                data.setRiskLevelName(riskLevelName);
                
                data.setDoctorName(getCellValue(row.getCell(colNum++)));
                
                if (data.getName() != null && !data.getName().isEmpty()) {
                    dataList.add(data);
                }
            }
        }
        
        return dataList;
    }

    private static String getCellValue(Cell cell) {
        if (cell == null) {
            return null;
        }
        switch (cell.getCellType()) {
            case STRING:
                return cell.getStringCellValue().trim();
            case NUMERIC:
                if (DateUtil.isCellDateFormatted(cell)) {
                    return cell.getDateCellValue().toString();
                } else {
                    return String.valueOf((long) cell.getNumericCellValue());
                }
            case BOOLEAN:
                return String.valueOf(cell.getBooleanCellValue());
            case FORMULA:
                return cell.getCellFormula();
            default:
                return null;
        }
    }

    public static class PatientExportData {
        private String patientNo;
        private String name;
        private Integer gender;
        private LocalDate birthday;
        private String idCard;
        private String phone;
        private String address;
        private String diseaseType;
        private LocalDate diagnosisDate;
        private String riskLevelName;
        private String doctorName;

        public String getPatientNo() { return patientNo; }
        public void setPatientNo(String patientNo) { this.patientNo = patientNo; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public Integer getGender() { return gender; }
        public void setGender(Integer gender) { this.gender = gender; }
        public LocalDate getBirthday() { return birthday; }
        public void setBirthday(LocalDate birthday) { this.birthday = birthday; }
        public String getIdCard() { return idCard; }
        public void setIdCard(String idCard) { this.idCard = idCard; }
        public String getPhone() { return phone; }
        public void setPhone(String phone) { this.phone = phone; }
        public String getAddress() { return address; }
        public void setAddress(String address) { this.address = address; }
        public String getDiseaseType() { return diseaseType; }
        public void setDiseaseType(String diseaseType) { this.diseaseType = diseaseType; }
        public LocalDate getDiagnosisDate() { return diagnosisDate; }
        public void setDiagnosisDate(LocalDate diagnosisDate) { this.diagnosisDate = diagnosisDate; }
        public String getRiskLevelName() { return riskLevelName; }
        public void setRiskLevelName(String riskLevelName) { this.riskLevelName = riskLevelName; }
        public String getDoctorName() { return doctorName; }
        public void setDoctorName(String doctorName) { this.doctorName = doctorName; }
    }

    public static class PatientImportData {
        private String patientNo;
        private String name;
        private Integer gender;
        private LocalDate birthday;
        private String idCard;
        private String phone;
        private String address;
        private String diseaseType;
        private LocalDate diagnosisDate;
        private String riskLevelName;
        private String doctorName;

        public String getPatientNo() { return patientNo; }
        public void setPatientNo(String patientNo) { this.patientNo = patientNo; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public Integer getGender() { return gender; }
        public void setGender(Integer gender) { this.gender = gender; }
        public LocalDate getBirthday() { return birthday; }
        public void setBirthday(LocalDate birthday) { this.birthday = birthday; }
        public String getIdCard() { return idCard; }
        public void setIdCard(String idCard) { this.idCard = idCard; }
        public String getPhone() { return phone; }
        public void setPhone(String phone) { this.phone = phone; }
        public String getAddress() { return address; }
        public void setAddress(String address) { this.address = address; }
        public String getDiseaseType() { return diseaseType; }
        public void setDiseaseType(String diseaseType) { this.diseaseType = diseaseType; }
        public LocalDate getDiagnosisDate() { return diagnosisDate; }
        public void setDiagnosisDate(LocalDate diagnosisDate) { this.diagnosisDate = diagnosisDate; }
        public String getRiskLevelName() { return riskLevelName; }
        public void setRiskLevelName(String riskLevelName) { this.riskLevelName = riskLevelName; }
        public String getDoctorName() { return doctorName; }
        public void setDoctorName(String doctorName) { this.doctorName = doctorName; }
    }
}
