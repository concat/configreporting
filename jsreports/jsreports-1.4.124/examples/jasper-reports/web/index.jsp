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

<!doctype html>
<html>
<head>
    <link href='http://fonts.googleapis.com/css?family=Merriweather:400,700,900,900italic,700italic,400italic,300italic,300' rel='stylesheet' type='text/css' />
    <link href="css/tomorrow-night-eighties.css" rel="stylesheet" type='text/css' />
    <link href="js/ditto/ditto.min.css" rel="stylesheet" type='text/css' />

    <style type="text/css">
        body {
            padding: 20px;
            margin: 0;
            font: 14px/22px "Merriweather", Georgia, serif;
            font-size-adjust: none;
            font-style: normal;
            font-variant: normal;
            font-weight: normal;
            background: #f4f6ec;
            color: #333;
        }
        .nav-category {
            color: #777;
            font-weight: normal;
            margin-bottom: 0.75em;
        }
        h1, h2, h3 {
            margin: 0;
            padding: 0;
        }

        .report-output {
            background: white;
            border: 1px solid #ccc;
            height: 400px;
        }

        .edit-link {
            font-size: 120%;
            margin-bottom: 10px;
        }

        code.hljs.javascript {
            border-radius: 5px;
            padding: 0.5em 0.85em;
        }
        pre {
            margin: 0;
        }

        textarea {
            display: block;
            width: 80%;
            height: 8em;
        }

        button {
            font-size: 120%;
            padding: 10px;
        }
    </style>
</head>
<body>
<a href="http://www.ditto.com" style="float:right">ditto home</a>
<h2 class="nav-category">ditto example</h2>

<h1>Jasper Reports Example</h1>

<hr />

<p>
    ditto report definition:
    <textarea class="ditto-def">Loading report definition...</textarea>
</p>

<p>
    <form action="executeReport.jsp" method="POST" accept-charset="">
        JasperReports report definition:
        <textarea name="jasperReportXml" class="jasper-def"></textarea>
    </form>
</p>

<p>
    <button class="convert-button" disabled="disabled">Convert and download as PDF</button>
</p>
<p>
    Convert to Jasper Reports format, send to the server, and use Jasper Reports to generate and download a PDF.
</p>
<p>
    See executeReport.jsp.
</p>

</body>
<script src="/js/highlight.pack.js" type="text/javascript"></script>
<script src="/js/jquery-1.11.0.min.js" type="text/javascript"></script>
<script src="/js/ditto/ditto.min.js" type="text/javascript"></script>
<script>

    // Load the report definition (here, a static file; in production, might be in a database)
    $.getJSON("ditto-report-def.json", function(def) {

        // Load the data source schema.  How you retrieve the schema is not important; all that's important
        // is that the JasperConverter is initialized with a dictionary of schema objects keyed by the data source ID,
        // so that the converter can find fields referenced by the report.  Any schemas that might
        // be in use by the report should be passed to the converter at instantiation time.
        $("textarea.ditto-def").val(JSON.stringify(def, undefined, 2));
        $.getJSON("/data/time-data-schema.json", function(schema) {
            // Now that we have a report definition object and a data source schema object, enable the button
            $("button.convert-button")
                .removeAttr("disabled")
                .on("click", function() {
                    // Convert to Jasper Reports format and send to the server
                    var jasperXml = (new ditto.JasperConverter({
                        schemas: { "time": schema }
                    })).convert(def);
                    $(".jasper-def").val(jasperXml);
                    $("form").submit();
                });
        });
    });

</script>
<script src="//static.getclicky.com/js" type="text/javascript"></script>
<script type="text/javascript">try{ if (location.href.toLowerCase().indexOf('ditto.com') > -1) { clicky.init(100739351); } } catch(e){}</script>
</html>