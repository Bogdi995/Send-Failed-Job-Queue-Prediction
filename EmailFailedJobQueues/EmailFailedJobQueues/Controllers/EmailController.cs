using Domain.Entities;
using Domain.Contracts;
using Microsoft.AspNetCore.Mvc;
using Service.Interfaces;

namespace EmailFailedJobQueues.Controllers
{
	[ApiController]
	[Route("api/controller")]
	public class EmailController(IEmailSender emailSender, ILoggerManager logger) : ControllerBase
	{
		private readonly IEmailSender _emailSender = emailSender;
		private readonly ILoggerManager _logger = logger;

        [HttpPost("SendFailedJobQueue")]
		public async Task<IActionResult> JobQueueFailed([FromBody] MessageJobQueue messageJobQueue)
		{
			await _emailSender.SendEmail(messageJobQueue);

			_logger.LogInfo($"The email was sent successfully.");
			
			return Ok();
		}

		[HttpPost("SendStoppedServerInstance")]
        public async Task<IActionResult> ServerInstanceStopped([FromBody] MessageServerInstance messageServerInstance)
		{
			await _emailSender.SendEmail(messageServerInstance);

			_logger.LogInfo($"The email was sent successfully.");

			return Ok();
		}
	}
}