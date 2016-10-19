/// <summary>
/// This class will read the serial port it is told and return a dictionary of tag, value pairs
/// 
/// </summary>

namespace WeatherStationReadDevice
{
    using System;
    using System.Collections.Generic;
    using System.IO.Ports;

    public class WeatherStationReadDevice
    {
        // this class will open port to weather station, accept current readings, and make values available
        private SerialPort serialPort;
        private string serialPortName;

        /// <summary>
        /// The constructor for this class
        /// </summary>
        /// <param name="portName">
        /// The port name will be like "COM1"
        /// </param>
        public WeatherStationReadDevice(string portName)
        {
            if (string.IsNullOrEmpty(portName))
            {
                throw new ArgumentNullException("portName");
            }
            serialPortName = portName;
        }

        private void OpenSerialPort()
        {
            try
            {
                serialPort.BaudRate = 9600;
                serialPort.DataBits = 8;
                serialPort.Handshake = Handshake.RequestToSend;
                serialPort.Parity = Parity.None;
                serialPort.ReadTimeout = 500;
                serialPort.StopBits = StopBits.One;
                serialPort.WriteTimeout = 50;

                serialPort.Open();
            }
            catch (Exception e)
            {
                throw new Exception("Error trying to open serial port", e);
            }
        }

        private void ClosePort()
        {
            if (serialPort.IsOpen)
            {
                serialPort.Close();
            }
        }

        /// <summary>
        /// The read serial port method
        /// </summary>
        /// <returns>
        /// Returns a dictionary of values, key = tag name + units
        /// </returns>
        public IDictionary<string, string> ReadSerialPort()
        {
            var dictionaryTagAndValueUnit = new Dictionary<string, string>();

            using (serialPort = new SerialPort(serialPortName))
            {
                OpenSerialPort();
                var buffer = string.Empty;
                do
                {
                    buffer = serialPort.ReadLine();
                    if (buffer.Contains("Running"))
                    {
                        continue;
                    }

                    if (buffer.Contains("Error"))
                    {
                        throw new Exception(buffer);
                    }

                    var bufferArray = buffer.Split(',');
                    if (!string.IsNullOrEmpty(bufferArray[0]))
                    {
                            
                        var tagAndUnits = string.IsNullOrEmpty(bufferArray[2]) 
                            ? string.Concat(bufferArray[0], "-", bufferArray[2])
                            : bufferArray[0];

                        var valueReturned = string.IsNullOrEmpty(bufferArray[1])
                            ? string.Empty
                            : bufferArray[1];

                        dictionaryTagAndValueUnit.Add(tagAndUnits, valueReturned);
                    }
                } while (buffer[0] != '*');

                serialPort.Close();
            }

            return dictionaryTagAndValueUnit;

        }
    }
}
