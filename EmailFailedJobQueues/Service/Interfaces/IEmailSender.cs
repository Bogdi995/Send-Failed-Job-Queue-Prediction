namespace Service.Interfaces
{
	public interface IEmailSender
	{
		Task SendEmail<T>(T message) where T : class;
	}
}
