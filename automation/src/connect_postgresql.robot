*** Settings ***
Library    DatabaseLibrary
Library    Collections

*** Variables ***
${DB_HOST}    localhost
${DB_PORT}    5432
${DB_NAME}    mydb
${DB_USER}    postgres
${DB_PASS}    mypassword

*** Keywords ***
Connect To Postgresql
    Connect To Database    psycopg2
    ...    ${DB_NAME}
    ...    ${DB_USER}
    ...    ${DB_PASS}
    ...    ${DB_HOST}
    ...    ${DB_PORT}

Disconnect From Database
    Disconnect From Database

Execute Query And Get Values
    [Arguments]    ${query}    ${columns}=${None}
    @{result}=    Execute SQL String    ${query}
    
    # Jika ${columns} adalah ${None}, kembalikan semua data hasil query
    IF    "${columns}" == "${None}"
        RETURN    @{result}
    END
    
    @{values}=    Create List
    FOR    ${row}    IN    @{result}
        ${row_values}=    Create List
        FOR    ${column}    IN    @{columns}
            ${value}=    Get From List    ${row}    ${column}
            Append To List    ${row_values}    ${value}
        END
        Append To List    ${values}    ${row_values}
    END
    RETURN    ${values}

*** Test Cases ***
Get All Values From Table
    Connect To Postgresql
    @{values}=    Execute Query And Get Values    SELECT * FROM mytable;    ${None}
    Log Many    @{values}
    Disconnect From Database

Get Specific Values From Table
    Connect To Postgresql
    @{columns}=    Create List    Nama    id
    @{values}=    Execute Query And Get Values    SELECT Nama, id FROM mytable;    @{columns}
    Log Many    @{values}
    Disconnect From Database