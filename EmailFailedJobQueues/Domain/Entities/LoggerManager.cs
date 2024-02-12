using Domain.Contracts;
using NLog;

namespace Domain.Entities
{
	public class LoggerManager : ILoggerManager
	{
        private static readonly ILogger logger = LogManager.GetCurrentClassLogger();
		public void LogDebug(string message) => logger.Debug(message);
		public void LogInfo(string message) => logger.Info(message);
		public void LogWarn(string message) => logger.Warn(message);
		public void LogError(string message) => logger.Error(message);
	}
}
