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
                    ToolTip = 'Specify the recipient for the email.';
                }
                field(Cc1; Rec.Cc1)
                {
                    ToolTip = 'Specify the first carbon copy recipient for the email.';
                }
                field(Cc2; Rec.Cc2)
                {
                    ToolTip = 'Specify the second carbon copy recipient for the email.';
                }
                field(Cc3; Rec.Cc3)
                {
                    ToolTip = 'Specify the third carbon copy recipient for the email.';
                }
                field(Url; Rec.Url)
                {
                    ToolTip = 'Specify the url the web requests are sent to.';
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