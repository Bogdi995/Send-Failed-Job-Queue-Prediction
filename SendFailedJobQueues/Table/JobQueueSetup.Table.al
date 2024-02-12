table 50100 "Job Queue Setup"
{
    Caption = 'Job Queue Setup';
    DataPerCompany = false;
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Primary Key"; Integer)
        {
            Caption = 'Primary Key';
            Editable = false;
            DataClassification = CustomerContent;
        }
        field(10; To; Text[80])
        {
            Caption = 'To';
            ExtendedDatatype = EMail;
            DataClassification = CustomerContent;
        }
        field(20; Cc1; Text[80])
        {
            Caption = 'Cc1';
            ExtendedDatatype = EMail;
            DataClassification = CustomerContent;
        }
        field(30; Cc2; Text[80])
        {
            Caption = 'Cc2';
            ExtendedDatatype = EMail;
            DataClassification = CustomerContent;
        }
        field(40; Cc3; Text[80])
        {
            Caption = 'Cc3';
            ExtendedDatatype = EMail;
            DataClassification = CustomerContent;
        }
        field(50; Url; Text[512])
        {
            Caption = 'Url';
            ExtendedDatatype = URL;
            DataClassification = CustomerContent;
        }
    }

    keys
    {
        key(Key1; "Primary Key")
        {
            Clustered = true;
        }
    }

    fieldgroups
    {
        fieldgroup(DropDown; To, Cc1, Cc2, Cc3, Url) { }
        fieldgroup(Brick; To, Cc1, Cc2, Cc3, Url) { }
    }
}