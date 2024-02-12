namespace Domain.Entities
{
	public class MessageServerInstance(string to, List<string> cc, string serverInstance, string state, string serviceAccount, string databaseServer, string databaseName)
    {
        public string To { get; set; } = to;
        public List<string> Cc { get; set; } = cc;
        public string ServerInstance { get; set; } = serverInstance;
        public string State { get; set; } = state;
        public string ServiceAccount { get; set; } = serviceAccount;
        public string DatabaseServer { get; set; } = databaseServer;
        public string DatabaseName { get; set; } = databaseName;
    }
}
