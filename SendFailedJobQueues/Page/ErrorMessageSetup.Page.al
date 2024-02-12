page 50102 "Error Message Setup"
{
    Caption = 'Error Message Setup';
    PageType = Card;
    ApplicationArea = All;
    UsageCategory = Administration;
    SourceTable = "Error Message Setup";
    InsertAllowed = false;
    DeleteAllowed = false;

    layout
    {
        area(Content)
        {
            group(General)
            {
                field("Error Message"; Rec."Error Message")
                {
                    ToolTip = 'Specify the error message that will be returned by the job queue.';
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