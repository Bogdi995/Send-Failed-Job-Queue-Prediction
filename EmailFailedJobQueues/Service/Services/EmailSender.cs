using Domain.Entities;
using MailKit.Net.Smtp;
using Microsoft.Extensions.Configuration;
using MimeKit;
using Newtonsoft.Json.Linq;
using Service.Interfaces;

namespace Service.Services
{
	public class EmailSender(EmailConfiguration emailConfiguration, IConfiguration configuration) : IEmailSender
	{
		private readonly EmailConfiguration _emailConfiguration = emailConfiguration;
		private readonly IConfiguration _configuration = configuration;

        public async Task SendEmail<T>(T message, string responseContent) where T : class 
		{
			var emailMessage = CreateEmailMessage(message, responseContent);

			await Send(emailMessage);
		}

		private MimeMessage CreateEmailMessage<T>(T message, string responseContent) where T : class
		{
			MimeMessage emailMessage = new();

			switch (typeof(T).Name)
			{
				case nameof(MessageJobQueue):
					MessageJobQueue messageJobQueue = (MessageJobQueue)Convert.ChangeType(message, typeof(MessageJobQueue));
					string possibleSolution = GetPossibleSolution(responseContent, messageJobQueue.ConfidenceLimit);
					emailMessage = CreateEmailJobQueue(messageJobQueue, possibleSolution);
					break;

				case nameof(MessageServerInstance):
					MessageServerInstance messageServerInstance = (MessageServerInstance)Convert.ChangeType(message, typeof(MessageServerInstance));
					emailMessage = CreateEmailServerInstance(messageServerInstance);
					break;
			}

			return emailMessage;
		}

		private MimeMessage CreateEmailJobQueue(MessageJobQueue messageJobQueue, string possibleSolution)
		{
			var emailMessage = new MimeMessage();

			emailMessage.From.Add(MailboxAddress.Parse(_emailConfiguration.From));
			emailMessage.To.Add(MailboxAddress.Parse(messageJobQueue.To));
			emailMessage.Cc.AddRange(messageJobQueue.Cc.Select(x => MailboxAddress.Parse(x)));
			emailMessage.Subject = _configuration.GetSection("JobQueueMailSubject").Value;
			var bodyBuilder = new BodyBuilder
			{
				HtmlBody = GetTextJobQueueFailed(messageJobQueue, possibleSolution)
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
			
			await client.ConnectAsync(_emailConfiguration.SmtpServer, _emailConfiguration.Port, true);
			await client.AuthenticateAsync(_emailConfiguration.UserName, _emailConfiguration.Password);
			await client.SendAsync(mailMessage);
			await client.DisconnectAsync(true);
			client.Dispose();
		}

		private string GetTextJobQueueFailed(MessageJobQueue messageJobQueue, string possibleSolution)
		{
			string mailText = GetMailText(_configuration.GetSection("JobQueueTemplate").Value);

			return mailText.Replace("[Company]", messageJobQueue.Company)
				.Replace("[Type]", messageJobQueue.ObjectType)
				.Replace("[ID]", messageJobQueue.ObjectId)
				.Replace("[Description]", messageJobQueue.ObjectDescription)
				.Replace("[StartDateTime]", messageJobQueue.StartDateTime.ToString())
				.Replace("[Duration]", messageJobQueue.Duration)
				.Replace("[ErrorMessage]", messageJobQueue.ErrorMessage)
				.Replace("[PossibleSolution]", possibleSolution);
		}

		private string GetTextServerInstanceStopped(MessageServerInstance messageServerInstance)
		{
			string mailText = GetMailText(_configuration.GetSection("ServiceInstanceTemplate").Value);

			return mailText.Replace("[ServerInstance]", messageServerInstance.ServerInstance)
				.Replace("[State]", messageServerInstance.State)
				.Replace("[ServiceAccount]", messageServerInstance.ServiceAccount)
				.Replace("[DatabaseServer]", messageServerInstance.DatabaseServer)
				.Replace("[DatabaseName]", messageServerInstance.DatabaseName);
		}

		private static string GetMailText(string path)
		{
			string filePath = Directory.GetCurrentDirectory() + path;
			StreamReader streamReader = new(filePath);
			string mailText = streamReader.ReadToEnd();
			streamReader.Close();

			return mailText;
		}

        private static string GetPossibleSolution(string responseContent, double confidenceLimit)
        {
            if (responseContent == "")
				return "Keine mögliche Lösung gefunden.";

            JObject jsonResponse = JObject.Parse(responseContent);
            double? confidence = (double?)jsonResponse["confidence"];

            if (confidence == null || confidence < confidenceLimit)
            {
                return "Keine mögliche Lösung gefunden.";
            }

            string? prediction = (string?)jsonResponse["prediction"];

            return prediction ?? "Keine mögliche Lösung gefunden.";
        }
    }
}
