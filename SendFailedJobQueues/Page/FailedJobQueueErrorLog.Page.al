page 50101 "Failed Job Queue Error Log"
{
    Caption = 'Failed Job Queue Error Log';
    PageType = List;
    ApplicationArea = All;
    UsageCategory = Administration;
    SourceTable = "Failed Job Queue Error Log";

    layout
    {
        area(Content)
        {
            repeater(General)
            {
                field("Error Message"; FailedJobQueueManagement.GetErrorMessage(Rec))
                {
                    Caption = 'Error Message';
                    ToolTip = 'Specifies the error message from the failed job queues.';
                }
                field("Date and Time"; Rec."Date and Time")
                {
                    ToolTip = 'Specifies the date and time when the job queue failed.';
                }
                field("User ID"; Rec."User ID")
                {
                    ToolTip = 'Specifies the user on which name was the job queue that failed.';
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(ShowErrorMessage)
            {
                Caption = 'Show error message';
                Image = ErrorLog;

                trigger OnAction()
                begin
                    Message(FailedJobQueueManagement.GetErrorMessage(Rec));
                end;
            }
        }

        area(Promoted)
        {
            group(Category_Process)
            {
                actionref(ShowErrorMessage_Promoted; ShowErrorMessage) { }
            }
        }
    }

    var
        FailedJobQueueManagement: Codeunit "Failed Job Queue Management";
}