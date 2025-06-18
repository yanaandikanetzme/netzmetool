*** Settings ***
Library    RequestsLibrary
Library    Collections

*** Variables ***
${BASE_URL}    http://api.example.com

*** Keywords ***
Send HTTP Request And Get Parameters
    [Arguments]    ${method}    ${endpoint}    ${data}=${None}    ${headers}=${None}    ${parameters}=${None}
    ${session}=    Create Session    my_session    ${BASE_URL}
    ${response}=    Run Keyword If    '${headers}' != '${None}'    ${method} On Session    my_session    ${endpoint}    data=${data}    headers=${headers}
    ...    ELSE    ${method} On Session    my_session    ${endpoint}    data=${data}
    ${json_response}=    Set Variable    ${response.json()}

    # Jika tidak ada parameter yang diberikan, kembalikan seluruh respons JSON
    IF    "${parameters}" == "${None}"
        RETURN    ${json_response}
    END

    ${result}=    Create Dictionary
    FOR    ${param}    IN    @{parameters}
        ${value}=    Get From Dictionary    ${json_response}    ${param}
        Run Keyword If    '${value}' == 'None'    Set To Dictionary    ${result}    ${param}    ${None}
        ...    ELSE    Set To Dictionary    ${result}    ${param}    ${value}
    END
    RETURN    ${result}

*** Test Cases ***
Get Parameters From GET Response With Headers
    ${headers}=    Create Dictionary    Authorization=Bearer token123
    ${parameters}=    Create List    name    id
    ${result}=    Send HTTP Request And Get Parameters    GET    /users/1    ${None}    ${headers}    ${parameters}
    Log    ${result}

Get Full GET Response Without Headers
    ${response}=    Send HTTP Request And Get Parameters    GET    /users/1    ${None}    ${None}
    Log    ${response}

Get Parameters From POST Response With Headers
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Bearer token123
    ${data}=    Create Dictionary    name=John    age=30
    ${parameters}=    Create List    name    id
    ${result}=    Send HTTP Request And Get Parameters    POST    /users    ${data}    ${headers}    ${parameters}
    Log    ${result}