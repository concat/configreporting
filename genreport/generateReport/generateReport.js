var fs = require('fs');
var path = require('path');
var AWS = require('aws-sdk');
var jsreports = require('./lib/jsreports/jsreports-server.min.js');

var myBucket = process.env.S3_BUCKET;
var myReportDef = process.env.REPORT_DEF;
var myReportSchema = process.env.REPORT_SCHEMA;
var myDataSource = process.env.DATA_SOURCE;
var myResourceDetailData = process.env.RESOURCE_DETAIL_DATA;
var myReportOutputFormat = process.env.REPORT_OUTPUT_FORMAT;
var myReportOutputFilename = process.env.REPORT_OUTPUT_FILENAME;
var myReportKey = "";

//var s3 = new AWS.S3();

/** Create a jsreports Server instance */
var server = new jsreports.Server();

function localname(str, sep) {
  return '/tmp/' + str.substr(str.lastIndexOf(sep) + 1 );
}

// Write the S3 Object to a file in /tmp
function getFile(s3key) {
	var filename = localname(s3key, '/');
  // console.log("The fullpath of the filename in the tmp directory is " + filename);

	var outfile = fs.createWriteStream(filename);
  // outfile.on('close', function() {console.log("File " + filename + " has been closed");});

	var params = { Bucket: myBucket, Key: s3key };
  console.log("Bucket is " + myBucket + " and s3 object is " + s3key);

  var s3 = new AWS.S3();
	s3.getObject(params).createReadStream().pipe(outfile);

  return filename;
}

var myS3Files = { reportdef: { s3key: myReportDef }, reportschema: { s3key: myReportSchema }, datasource: { s3key: myDataSource }, resourcedetaildata: { s3key: myResourceDetailData }} ;


exports.handler = (event, context, callback) => {
/**
 * Load all json data needed to run the report from S3 buckets onto the /tmp directory.
 */


for (var prop in myS3Files) {
  myS3Files[prop]['localfilename'] = getFile(myS3Files[prop]['s3key']);
}

function waitandgo (myfunc, pause) {
  setTimeout (myfunc, pause);
}

waitandgo(generatePDF, 60000);

function generatePDF(){
var myreportdefcontents = require(myS3Files.reportdef.localfilename);
// console.log("Reportdef contents are " + JSON.stringify(myreportdefcontents, null, 2));
var mydatasourcecontents = require(myS3Files.datasource.localfilename);
// console.log("Datasource contents are " + JSON.stringify(mydatasourcecontents, null, 2));


/**
 * Call server.export() just like you would call jsreports.export().
 * The last argument is a callback function that will be called with
 * a stream containing the PDF for reading.
 */
 server.start();
 server.export({
   format: myReportOutputFormat,
   report_def: myreportdefcontents,
   datasets:[ mydatasourcecontents ],
   /**
    * Must provide a file:// base URL to prepend to the image 
    * URLs in the report, in order to locate them on the server - 
    * here, expect images to be in the current directory
    */
   imageUrlPrefix: 'file:///tmp/'
}, function(err, pdfStream) {
  if (err) return console.error(err);
  /**
   * At this point we have the PDF available for reading
   * in pdfStream.  Write it to the path specified at 
   * the command line
   */
  var s3out = new AWS.S3();
  var outPath = '/tmp/thisReport';
  var outStream = fs.createWriteStream(outPath, 'utf8');
  outStream.on('close', function() {
    console.log('Wrote ' + myReportOutputFormat + ' to', outPath);
    myReportKey = myReportOutputFilename + new Date().getTime() + "." + myReportOutputFormat;
    var readpdfstream = fs.createReadStream(outPath);
    readpdfstream.on('open', function(){
        var pdfparams = { Bucket: myBucket, Key: myReportKey, Body: readpdfstream};
        s3out.putObject(pdfparams, function(err, data) {
        if (err) {
          console.log(err);
          callback(err);
        }
        else {
          console.log(data);
          var jsonoutput = { "s3bucketobjkey": myReportKey };
          callback(null, jsonoutput);
        }
        });
      });
    server.stop();
    });
    pdfStream.pipe(outStream);
  });
 }
}