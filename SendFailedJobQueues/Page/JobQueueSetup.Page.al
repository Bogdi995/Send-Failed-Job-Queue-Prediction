page 50100 "Job Queue Setup"
{
    Caption = 'Job Queue Setup';
    PageType = Card;
    ApplicationArea = All;
    UsageCategory = Administration;
    SourceTable = "Job Queue Setup";
    InsertAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            group(General)
            {
                field(To; Rec."To")
                {
                    ToolTip = 'Specifies the recipient for the email.';
                }
                field(Cc1; Rec.Cc1)
                {
                    ToolTip = 'Specifies the first carbon copy recipient for the email.';
                }
                field(Cc2; Rec.Cc2)
                {
                    ToolTip = 'Specifies the second carbon copy recipient for the email.';
                }
                field(Cc3; Rec.Cc3)
                {
                    ToolTip = 'Specifies the third carbon copy recipient for the email.';
                }
                field(Url; Rec.Url)
                {
                    ToolTip = 'Specifies the url the web requests are sent to.';
                }
                field(ConfidenceLimit; Rec."Confidence Limit")
                {
                    ToolTip = 'Specifies the minimum confidence limit that the AI must meet to send a possible error resolution.';
                }
            }
        }
    }

    trigger OnOpenPage()
    begin
        Rec.Reset();

        if not Rec.Get() then begin
            Rec.Init();
            Rec.Insert();
        end;
    end;
}