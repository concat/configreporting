package ditto;

import java.sql.*;
import java.util.*;

/**
 * Demonstrates how to save user-defined reports in a database.  This example uses the Java
 * Derby database (JavaDB) and simple JDBC calls to store the reports in a table.
 */
public class DataProvider {

    private static final String _driverName = "org.apache.derby.jdbc.EmbeddedDriver";
    private static Object _driverInstance;

    public DataProvider() {
        requireDatabase();
    }

    /**
     * Creates the database and tables, if they don't already exist.
     */
    private void createDatabase() {
        Connection conn = getDBConnection();
        try {
            DatabaseMetaData metaData = conn.getMetaData();
            ResultSet rs = metaData.getTables(null, null, "TIME", null);
            if (!rs.next()) {
                Statement st = conn.createStatement();
                st.execute("create table time(id int NOT NULL GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1), " +
                        "Entry_Date date, " +
                        "Current_timesheet_status varchar(250), " +
                        "Full_name varchar(250), " +
                        "Employee_number varchar(250), " +
                        "Person_status varchar(250), " +
                        "Employment_type varchar(250), " +
                        "Client_name varchar(250), " +
                        "Client_short_name varchar(250), " +
                        "Client_Status varchar(250), " +
                        "Job_name varchar(250), " +
                        "Job_number varchar(250), " +
                        "Job_status varchar(250), " +
                        "Hours decimal, " +
                        "Comment varchar(250), " +
                        "Task_name varchar(250), " +
                        "Task_code varchar(250), " +
                        "Task_status varchar(250), " +
                        "Job_billable boolean" +
                        "Billing_rate decimal, " +
                        "Cost decimal, " +
                        "Estimated_job_time decimal, " +
                        "Time_Entry_ID varchar(250), " +
                        "Timesheet_ID varchar(250), " +
                        "Person_ID varchar(250), " +
                        "Client_ID varchar(250), " +
                        "Job_ID varchar(250), " +
                        "Task_ID varchar(250), " +
                    ")");
                conn.commit();
            }
        } catch(SQLException sqlex) {
            rollback(conn);
            throw new RuntimeException(sqlex);
        }
    }

    private void requireDatabase() {
        createDatabase();
    }

    private static Connection getDBConnection() {
        Connection conn = null;
        try {
            if (_driverInstance == null) {
                _driverInstance = Class.forName(_driverName).newInstance();
            }
            conn = DriverManager.getConnection("jdbc:derby:derbyDB;create=true");
            conn.setAutoCommit(false);
        } catch(Exception ex) {
            rollback(conn);
            throw new RuntimeException(ex);
        }
        return conn;
    }

    private static void rollback(Connection conn) {
        try {
            conn.rollback();
        } catch(Exception ex) {
            throw new RuntimeException(ex);
        }
    }

}