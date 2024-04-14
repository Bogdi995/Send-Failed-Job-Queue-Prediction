codeunit 50101 "Codeunit with Errors Example"
{
    trigger OnRun()
    var
        ErrorMessageSetup: Record "Error Message Setup";
    begin
        if ErrorMessageSetup.Get() then
            Error(ErrorMessageSetup."Error Message");
    end;
}