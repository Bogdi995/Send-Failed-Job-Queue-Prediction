using Domain.Entities;
using MailKit.Net.Smtp;
using Microsoft.Extensions.Configuration;
using MimeKit;
using Service.Interfaces;

namespace Service.Services
{
	public class EmailSender(EmailConfiguration emailConfiguration, IConfiguration configuration) : IEmailSender
	{
		private readonly EmailConfiguration _emailConfiguration = emailConfiguration;
		private readonly IConfiguration _configuration = configuration;

        public async Task SendEmail<T>(T message) where T : class 
		{
			var emailMessage = CreateEmailMessage(message);

			await Send(emailMessage);
		}

		private MimeMessage CreateEmailMessage<T>(T message) where T : class
		{
			MimeMessage emailMessage = new();

			switch (typeof(T).Name)
			{
				case nameof(MessageJobQueue):
					MessageJobQueue messageJobQueue = (MessageJobQueue)Convert.ChangeType(message, typeof(MessageJobQueue));
					emailMessage = CreateEmailJobQueue(messageJobQueue);
					break;

				case nameof(MessageServerInstance):
					MessageServerInstance messageServerInstance = (MessageServerInstance)Convert.ChangeType(message, typeof(MessageServerInstance));
					emailMessage = CreateEmailServerInstance(messageServerInstance);
					break;
			}

			return emailMessage;
		}

		private MimeMessage CreateEmailJobQueue(MessageJobQueue messageJobQueue)
		{
			var emailMessage = new MimeMessage();

			emailMessage.From.Add(MailboxAddress.Parse(_emailConfiguration.From));
			emailMessage.To.Add(MailboxAddress.Parse(messageJobQueue.To));
			emailMessage.Cc.AddRange(messageJobQueue.Cc.Select(x => MailboxAddress.Parse(x)));
			emailMessage.Subject = _configuration.GetSection("JobQueueMailSubject").Value;
			var bodyBuilder = new BodyBuilder
			{
				HtmlBody = GetTextJobQueueFailed(messageJobQueue)
			};
			emailMessage.Body = bodyBuilder.ToMessageBody();

			return emailMessage;
		}

		private MimeMessage CreateEmailServerInstance(MessageServerInstance messageServerInstance)
		{
			var emailMessage = new MimeMessage();

			emailMessage.From.Add(MailboxAddress.Parse(_emailConfiguration.From));
			emailMessage.To.Add(MailboxAddress.Parse(messageServerInstance.To));
			emailMessage.Cc.AddRange(messageServerInstance.Cc.Select(x => MailboxAddress.Parse(x)));
			emailMessage.Subject = _configuration.GetSection("ServerInstanceMailSubject").Value;
			var bodyBuilder = new BodyBuilder
			{
				HtmlBody = GetTextServerInstanceStopped(messageServerInstance)
			};
			emailMessage.Body = bodyBuilder.ToMessageBody();

			return emailMessage;
		}

		private async Task Send(MimeMessage mailMessage)
		{
			using var client = new SmtpClient();
			
			await client.ConnectAsync(_emailConfiguration.SmtpServer);
			await client.AuthenticateAsync(_emailConfiguration.UserName, _emailConfiguration.Password);
			await client.SendAsync(mailMessage);
			await client.DisconnectAsync(true);
			client.Dispose();
		}

		private string GetTextJobQueueFailed(MessageJobQueue messageJobQueue)
		{
			string mailText = GetMailText(_configuration.GetSection("JobQueueTemplate").Value);

			return mailText.Replace("[Mandant]", messageJobQueue.Company)
				.Replace("[Art]", messageJobQueue.ObjectType)
				.Replace("[ID]", messageJobQueue.ObjectId)
				.Replace("[Beschriftung]", messageJobQueue.ObjectDescription)
				.Replace("[Startdatum/-uhrzeit]", messageJobQueue.StartDateTime.ToString())
				.Replace("[Dauer]", messageJobQueue.Duration)
				.Replace("[Fehlermeldung]", messageJobQueue.ErrorMessage);
		}

		private string GetTextServerInstanceStopped(MessageServerInstance messageServerInstance)
		{
			string mailText = GetMailText(_configuration.GetSection("ServiceInstanceTemplate").Value);

			return mailText.Replace("[Server Instance]", messageServerInstance.ServerInstance)
				.Replace("[State]", messageServerInstance.State)
				.Replace("[Service Account]", messageServerInstance.ServiceAccount)
				.Replace("[Database Server]", messageServerInstance.DatabaseServer)
				.Replace("[Database Name]", messageServerInstance.DatabaseName);
		}

		private static string GetMailText(string path)
		{
			string filePath = Directory.GetCurrentDirectory() + path;
			StreamReader streamReader = new(filePath);
			string mailText = streamReader.ReadToEnd();
			streamReader.Close();

			return mailText;
		}
	}
}
