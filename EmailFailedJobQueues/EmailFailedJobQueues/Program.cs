using EmailFailedJobQueues.Extensions;
using NLog;
using NLog.Extensions.Logging;

var builder = WebApplication.CreateBuilder(args);

builder.Configuration.AddJsonFile("appsettings.json", optional: false);
builder.Configuration.AddJsonFile("appsettings.Development.json", optional: true);

LogManager.LoadConfiguration(string.Concat(Directory.GetCurrentDirectory(), "/nlog.config"));
builder.Logging.ClearProviders();
builder.Logging.AddNLog();

builder.Services.ConfigureLoggerService();
builder.Services.ConfigureEmailService(builder.Configuration);
builder.Services.ConfigureEmailSender();
builder.Services.AddControllers();

var app = builder.Build();

app.ConfigureCustomExceptionMiddleware();

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
