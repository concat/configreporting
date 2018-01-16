<%@ page contentType="text/html;charset=UTF-8" language="java" %>

<%@ page import="net.sf.jasperreports.engine.*" %>
<%@ page import="java.util.*" %>
<%@ page import="javax.servlet.*" %>
<%@ page import="java.io.ByteArrayInputStream" %>
<%@ page import="java.io.InputStream" %>
<%@ page import="java.nio.charset.StandardCharsets" %>
<%@ page import="java.sql.Connection" %>
<%@ page import="java.sql.DriverManager" %>
<%@ page import="java.sql.Statement" %>
<%@ page import="java.sql.ResultSet" %>
<%@ page import="org.relique.jdbc.csv.CsvDriver" %>

<html>
  <head>
    <title></title>
  </head>
  <body>
<%
    String jrxml = request.getParameter("jasperReportXml");
    try {
        // For this demo, we use a JDBC driver that loads data from the time-data.csv file.  You would
        // use your own Jasper-compatible data source here.
        Class.forName("org.relique.jdbc.csv.CsvDriver");
        Properties props = new Properties();
        // Since it's a CSV file, we need to manually declare the data types.  Not necessary for most data sources.
        props.put("columnTypes", "Date,String,String,String,String,String,String,String,String,BigDecimal,String,BigDecimal,BigDecimal,String,String,String,String,String,String");
        props.put("dateFormat", "M/d/yyyy");
        Connection conn = DriverManager.getConnection("jdbc:relique:csv:" + application.getRealPath("/data"), props);
        Statement stmt = conn.createStatement();
        ResultSet results = stmt.executeQuery("SELECT * FROM time-data");

        // Read the JRXML report definition (produced by ditto) from a string, and then compile
        // and run it like any other Jasper report.
        InputStream stream = new ByteArrayInputStream(jrxml.getBytes(StandardCharsets.UTF_8));
        results.next();
        JasperReport jasperReport = JasperCompileManager.compileReport(stream);
        HashMap<String, Object> params = new HashMap<String, Object>();
        JasperPrint jasperPrint =
                JasperFillManager.fillReport(jasperReport, params, new JRResultSetDataSource(results));

        // Send the resulting PDF to the browser as a download
        response.setContentType("application/octet-stream");
        response.setHeader("Content-Disposition", "Attachment;Filename=\"jasper-report.pdf\"");
        ServletOutputStream sos = response.getOutputStream();
        JasperExportManager.exportReportToPdfStream(jasperPrint, sos);
    } catch(Exception exc) {
        throw new RuntimeException(exc);
    }
%>
  </body>
</html>