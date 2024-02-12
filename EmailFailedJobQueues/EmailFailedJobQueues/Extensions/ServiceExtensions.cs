using Domain.Contracts;
using Domain.Entities;
using EmailFailedJobQueues.CustomExceptionMiddleware;
using Service.Interfaces;
using Service.Services;

namespace EmailFailedJobQueues.Extensions
{
    public static class ServiceExtensions
	{
		public static void ConfigureLoggerService(this IServiceCollection services)
		{
			services.AddSingleton<ILoggerManager, LoggerManager>();
		}

		public static void ConfigureEmailService(this IServiceCollection services, IConfiguration configuration)
		{
			var emailConfig = configuration
				.GetSection("EmailConfiguration")
				.Get<EmailConfiguration>();

			if (emailConfig != null)
				services.AddSingleton(emailConfig);
		}

		public static void ConfigureEmailSender(this IServiceCollection services)
		{
			services.AddScoped<IEmailSender ,EmailSender>();
		}

		public static void ConfigureCustomExceptionMiddleware(this WebApplication app)
		{
			app.UseMiddleware<ExceptionMiddleware>();
		}
	}
}
