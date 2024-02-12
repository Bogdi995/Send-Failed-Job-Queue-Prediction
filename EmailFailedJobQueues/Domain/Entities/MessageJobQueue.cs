namespace Domain.Entities
{
    public class MessageJobQueue(string to, List<string> cc, string company, string objectType, string objectId, string objectDescription, DateTime startDateTime, string duration, string errorMessage)
    {
        public string To { get; set; } = to;
        public List<string> Cc { get; set; } = cc;
        public string Company { get; set; } = company;
        public string ObjectType { get; set; } = objectType;
        public string ObjectId { get; set; } = objectId;
        public string ObjectDescription { get; set; } = objectDescription;
        public DateTime StartDateTime { get; set; } = startDateTime;
        public string Duration { get; set; } = duration;
        public string ErrorMessage { get; set; } = errorMessage;
    }
}
