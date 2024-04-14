using Domain.Entities;
using Domain.Contracts;
using Microsoft.AspNetCore.Mvc;
using Service.Interfaces;

namespace EmailFailedJobQueues.Controllers
{
	[ApiController]
	[Route("api/controller")]
	public class EmailController(IEmailSender emailSender, ILoggerManager logger, IConfiguration configuration) : ControllerBase
	{
		private readonly IEmailSender _emailSender = emailSender;
		private readonly ILoggerManager _logger = logger;
		private readonly IConfiguration _configuration = configuration;

        [HttpPost("SendFailedJobQueue")]
		public async Task<IActionResult> JobQueueFailed([FromBody] MessageJobQueue messageJobQueue)
		{
			string responseContent = "";
			HttpClient httpClient = new();

			var response = await httpClient.PostAsJsonAsync(_configuration.GetSection("NLPModelUrl").Value, new { errorMessage = messageJobQueue.ErrorMessage });
			if (response.IsSuccessStatusCode)
			{
				responseContent = await response.Content.ReadAsStringAsync();
			}

			await _emailSender.SendEmail(messageJobQueue, responseContent);

            _logger.LogInfo($"The email was sent successfully.");
			
			return Ok();
		}

		[HttpPost("SendStoppedServerInstance")]
        public async Task<IActionResult> ServerInstanceStopped([FromBody] MessageServerInstance messageServerInstance)
		{
			await _emailSender.SendEmail(messageServerInstance, "");

			_logger.LogInfo($"The email was sent successfully.");

			return Ok();
		}
	}
}