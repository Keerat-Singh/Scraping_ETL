# Scraping ETL Project
 This project is an ETL (Extract, Transform, Load) process created with SQL Server Integration Services (SSIS). It includes dynamic configurations, error handling, and database management. The package reads data from CSV files, checks for the existence of tables, and inserts or updates data within SQL Server. This README provides an overview of the project setup, configuration, and deployment.

Configuration for Book_Intigration.sln package:
1. Ensure SQL Server is installed and accessible.
2. Update the user and package variable to point towards your specific directory.
3. The user variable 'CSVExportedFileName' in package should match the 'csv_file_name' in book.py file.
4. Create an empty table in your database with name 'dbo.book' name with book_test.csv file to ensure an empty table creation. You would need to make this selection within OLE DB Destination Editor in Data Flow in your Book_Intigration.sln file.
