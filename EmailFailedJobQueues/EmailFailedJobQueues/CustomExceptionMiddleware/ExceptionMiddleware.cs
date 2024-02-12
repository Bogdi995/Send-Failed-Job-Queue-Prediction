using Domain.Contracts;
using Domain.Entities;
using System.Net;

namespace EmailFailedJobQueues.CustomExceptionMiddleware
{
	public class ExceptionMiddleware(RequestDelegate next, ILoggerManager logger)
    {
		private readonly RequestDelegate _next = next;
		private readonly ILoggerManager _logger = logger;

        public async Task InvokeAsync(HttpContext httpContext)
		{
			try
			{
				await _next(httpContext);
			}
			catch (Exception ex)
			{
				_logger.LogError($"Something went wrong: {ex}");
				await HandleExceptionAsync(httpContext);
			}
		}

		private static Task HandleExceptionAsync(HttpContext httpContext) 
		{
			httpContext.Response.ContentType = "application/json";
			httpContext.Response.StatusCode = (int)HttpStatusCode.InternalServerError;

			return httpContext.Response.WriteAsync(new ErrorDetails
			{
				StatusCode = httpContext.Response.StatusCode,
				Message = "Internal Server Error"
			}.ToString());
		}
	}
}
