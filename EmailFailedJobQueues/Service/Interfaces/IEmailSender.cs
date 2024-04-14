namespace Service.Interfaces
{
	public interface IEmailSender
	{
        Task SendEmail<T>(T message, string responseContent) where T : class;
	}
}
