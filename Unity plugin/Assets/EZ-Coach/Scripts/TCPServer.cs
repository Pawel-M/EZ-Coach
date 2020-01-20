using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Runtime.Serialization;
using System.Text;
using System.Threading;
using JetBrains.Annotations;
using UnityEngine;

namespace EZCoach {
    /// <summary>
    /// An exception class thrown if the connection is not established before sending a message.
    /// </summary>
    public class NotConnectedException : Exception {
        public NotConnectedException() { }
        protected NotConnectedException([NotNull] SerializationInfo info, StreamingContext context) : base(info, context) { }
        public NotConnectedException(string message) : base(message) { }
        public NotConnectedException(string message, Exception innerException) : base(message, innerException) { }
    }

    /// <summary>
    /// A class representing a TCP socket connection.
    /// </summary>
    public class TCPServer {
        private readonly int port;
        private readonly int bufferSize;
        private readonly Queue messages;
        private Thread connectionThread;
        private TcpListener tcpListener;
        private TcpClient tcpClient;
        private bool running = false;

        public TCPServer(int port, int bufferSize = 256) {
            this.port = port;
            this.bufferSize = bufferSize;
            messages = Queue.Synchronized(new Queue());
        }

        /// <summary>
        /// Starts the inner connection thread.
        /// </summary>
        public void Start() {
            connectionThread = new Thread(WaitForConnection);
            connectionThread.Start();
        }

        /// <summary>
        /// Stops the inner connection thread.
        /// </summary>
        public void Stop() {
            running = false;
            tcpListener.Stop();
            tcpClient = null;
            Debug.Log("TCP Server stopped");
        }

        /// <summary>
        /// Resets the connection.
        /// </summary>
        public void Restart() {
            Stop();
            Start();
        }

        /// <summary>
        /// Waits for the connection and if a client is connected, collects the messages and puts them into the messages queue.
        /// </summary>
        private void WaitForConnection() {
            running = true;
            tcpListener = new TcpListener(IPAddress.Loopback, port);
            tcpListener.Start();

            var bytes = new byte[bufferSize];

            while (running) {
                Debug.Log("Waiting for connection...");

                try {
                    using (tcpClient = tcpListener.AcceptTcpClient()) {
                        var stream = tcpClient.GetStream();
                        Debug.Log($"Client {tcpClient.Client.AddressFamily} connected.");
                        int i;
                        while ((i = stream.Read(bytes, 0, bytes.Length)) != 0) {
                            var data = Encoding.UTF8.GetString(bytes, 0, i);
//                            Debug.Log($"Received data: {data}");
                            messages.Enqueue(data);
                        }
                    }

                } catch (IOException exception) {
                    Debug.LogWarning($"TCP Server: IO exception: {exception}\n{exception.StackTrace}");
                } catch (SocketException exception) {
                    Debug.LogWarning($"TCP Server: socket exception: {exception}\n{exception.StackTrace}");
                }
            }
        }

        /// <summary>
        /// Sends the message to the client.
        /// </summary>
        /// <param name="message">a string containing the message to be sent</param>
        /// <exception cref="NotConnectedException">Thrown if not connected before sending the message.</exception>
        public void Send(string message) {
            if (!IsConnected)
                throw new NotConnectedException($"Error sending message {message} - disconnected.");
                
            var stream = tcpClient.GetStream();
            if (stream.CanWrite) {
//                Debug.Log($"TCP Server, sending message: {message}");
                byte[] messageBytes = Encoding.UTF8.GetBytes(message);
                stream.Write(messageBytes, 0, messageBytes.Length);
            } else {
                Debug.LogError("Can't write to stream!");
            }
        }

        /// <summary>
        /// Obtains messages from the queue. Returns a single string containing a message or null if not messages were present.
        /// </summary>
        /// <returns>a single message or null if no messages were present</returns>
        public string ObtainMessage() {
            if (messages.Count == 0)
                return null;

            return (string) messages.Dequeue();
        }

        /// <summary>
        /// Returns weather the server is connected.
        /// </summary>
        public bool IsConnected => tcpClient != null && tcpClient.Connected;
    }

}