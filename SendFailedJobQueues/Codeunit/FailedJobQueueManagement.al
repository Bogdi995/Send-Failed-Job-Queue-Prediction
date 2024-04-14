codeunit 50100 "Failed Job Queue Management"
{
    trigger OnRun()
    begin

    end;

    procedure GetErrorMessage(var FailedJobQueueErrorLog: Record "Failed Job Queue Error Log"): Text
    var
        StreamReader: DotNet StreamReader;
        Encoding: DotNet Encoding;
        IStream: InStream;
    begin
        FailedJobQueueErrorLog.CalcFields("Error Message");

        if FailedJobQueueErrorLog."Error Message".HasValue() then begin
            FailedJobQueueErrorLog."Error Message".CreateInStream(IStream);
            StreamReader := StreamReader.StreamReader(IStream, Encoding.UTF8, true);
            exit(StreamReader.ReadToEnd());
        end;
    end;

    [EventSubscriber(ObjectType::Table, Database::"Job Queue Entry", 'OnBeforeTryRunJobQueueSendNotification', '', true, true)]
    local procedure SendEmailOnBeforeTryRunJobQueueSendNotification(var JobQueueEntry: Record "Job Queue Entry"; var IsHandled: Boolean)
    begin
        SendPostRequest(JobQueueEntry);

        IsHandled := true;
    end;

    local procedure SendPostRequest(var JobQueueEntry: Record "Job Queue Entry")
    var
        Client: HttpClient;
        Headers: HttpHeaders;
        Content: HttpContent;
        RequestMessage: HttpRequestMessage;
        ResponseMessage: HttpResponseMessage;
        Response: Text;
    begin
        RequestMessage.SetRequestUri(GetPostUrl());
        RequestMessage.Method('POST');
        RequestMessage.GetHeaders(Headers);

        Content.WriteFrom(GetPayload(JobQueueEntry));
        Content.GetHeaders(Headers);
        if Headers.Contains('Content-Type') then
            Headers.Remove('Content-Type');
        Headers.Add('Content-Type', 'application/json');

        Client.Timeout(16000);
        RequestMessage.Content(Content);

        if not Client.Send(RequestMessage, ResponseMessage) then begin
            InsertErrorInLogTable(ResponseMessage.ReasonPhrase);
            exit;
        end;

        if not ResponseMessage.IsSuccessStatusCode then begin
            ResponseMessage.Content.ReadAs(Response);
            InsertErrorInLogTable(Response);
        end;
    end;

    local procedure GetPostUrl(): Text
    var
        JobQueueSetup: Record "Job Queue Setup";
    begin
        if JobQueueSetup.Get() then
            exit(JobQueueSetup.Url);
    end;

    local procedure GetPayload(var JobQueueEntry: Record "Job Queue Entry"): Text
    var
        JobQueueSetup: Record "Job Queue Setup";
        FailedJobQueueManagement: Codeunit "Failed Job Queue Management";
        JObject: JsonObject;
    begin
        if not JobQueueSetup.Get() then
            exit;

        JobQueueEntry.CalcFields("Object Caption to Run");

        JObject.Add('To', JobQueueSetup."To");
        JObject.Add('Cc', GetCcJsonArray(JobQueueSetup));
        JObject.Add('Company', CompanyName);
        JObject.Add('ObjectType', Format(JobQueueEntry."Object Type to Run"));
        JObject.Add('ObjectId', Format(JobQueueEntry."Object ID to Run"));
        JObject.Add('ObjectDescription', JobQueueEntry."Object Caption to Run");
        JObject.Add('StartDateTime', GetProcessedStartDateTime(JobQueueEntry));
        JObject.Add('Duration', Format(GetFilteredJobQueueLogEntry(JobQueueEntry.ID, JobQueueEntry."Maximum No. of Attempts to Run").Duration()));
        JObject.Add('ErrorMessage', JobQueueEntry."Error Message");
        JObject.Add('ConfidenceLimit', JobQueueSetup."Confidence Limit");

        exit(Format(JObject));
    end;

    local procedure GetCcJsonArray(var JobQueueSetup: Record "Job Queue Setup"): JsonArray
    var
        CcJsonArray: JsonArray;
    begin
        if JobQueueSetup.Cc1 <> '' then
            CcJsonArray.Add(JobQueueSetup.Cc1);

        if JobQueueSetup.Cc2 <> '' then
            CcJsonArray.Add(JobQueueSetup.Cc2);

        if JobQueueSetup.Cc3 <> '' then
            CcJsonArray.Add(JobQueueSetup.Cc3);

        exit(CcJsonArray);
    end;

    local procedure GetFilteredJobQueueLogEntry(JobQueueEntryId: Guid; MaxNoOfAttemptsToRun: Integer): Record "Job Queue Log Entry"
    var
        JobQueueLogEntry: Record "Job Queue Log Entry";
    begin
        JobQueueLogEntry.SetRange(ID, JobQueueEntryId);

        if JobQueueLogEntry.FindLast() then
            while MaxNoOfAttemptsToRun > 1 do begin
                JobQueueLogEntry.Next(-1);
                MaxNoOfAttemptsToRun -= 1;
            end;

        exit(JobQueueLogEntry);
    end;

    local procedure GetProcessedStartDateTime(var JobQueueEntry: Record "Job Queue Entry"): Text
    var
        JObject: JsonObject;
        DateToken: JsonToken;
        TimeToken: JsonToken;
        ProcessedDateTime: Text;
        StartDateTime: DateTime;
        StartDate: Date;
        StartTime: Time;
    begin
        StartDateTime := GetFilteredJobQueueLogEntry(JobQueueEntry.ID, JobQueueEntry."Maximum No. of Attempts to Run")."Start Date/Time";
        StartDate := DT2Date(StartDateTime);
        StartTime := DT2Time(StartDateTime);

        JObject.Add('Date', Today);
        JObject.Add('Time', Time);
        JObject.Get('Date', DateToken);
        JObject.Get('Time', TimeToken);

        ProcessedDateTime := DelChr(Format(DateToken), '=', '"') + 'T' + DelChr(Format(TimeToken), '=', '"');
        exit(ProcessedDateTime);
    end;

    local procedure InsertErrorInLogTable(ErrorMessage: Text)
    var
        FailedJobQueueErrorLog: Record "Failed Job Queue Error Log";
        OStream: OutStream;
    begin
        FailedJobQueueErrorLog.Init();
        FailedJobQueueErrorLog."Entry No." := 0;
        FailedJobQueueErrorLog."Error Message".CreateOutStream(OStream, TextEncoding::UTF8);
        OStream.WriteText(ErrorMessage);
        FailedJobQueueErrorLog."Date and Time" := CurrentDateTime;
        FailedJobQueueErrorLog."User ID" := UserId;
        FailedJobQueueErrorLog.Insert(true);
    end;
}