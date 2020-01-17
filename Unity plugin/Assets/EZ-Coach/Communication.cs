using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;

namespace EZCoach {
    /// <summary>
    /// The Communication is the center class of the plugin as by managing the TCPServer object it establishes the socket server for Training Module to connect to and is responsible for exchanging messages with it.
    /// The received messages are passed to the object that is implementing ICommunicationHandler interface (use handler field).
    /// The updateMethod field is used to select one of two update methods, namely, FixedUpdate and LateUpdate. This determine when received messages are parsed.
    /// Use SendManifest and SendStates methods to send the game's manifest and state observations respectively. 
    /// </summary>
    public class Communication : MonoBehaviour {

        public ICommunicationHandler handler;

        [SerializeField] private int port = 6666;
        [SerializeField] private UpdateMethod updateMethod = UpdateMethod.FixedUpdate;
        [SerializeField] private bool debugMessages;

        private TCPServer connection;

        void Start() {
            connection = new TCPServer(port);
            connection.Start();
        }

        private void OnDestroy() {
            connection.Stop();
        }

        void LateUpdate() {
            if (updateMethod != UpdateMethod.LateUpdate)
                return;

            UpdateInternal();
        }

        private void FixedUpdate() {
            if (updateMethod != UpdateMethod.FixedUpdate)
                return;

            UpdateInternal();
            ;
        }

        /// <summary>
        /// Invoked by LateUpdate or FixedUpdate methods (depending on the updateMethod field). Parses messages obtained from the connection.
        /// </summary>
        private void UpdateInternal() {
            var message = connection.ObtainMessage();
            if (message != null) {
                ParseMessage(message);
            }
        }

        /// <summary>
        /// Parses the message and then invokes methods of the ICommunicationHandler interface.
        /// </summary>
        /// <param name="message">the message obtained from the connection, in the form of JSON string</param>
        private void ParseMessage(string message) {
            if (debugMessages) {
                Debug.Log($"message: {message}");
            }

            var messageType = JsonConvert.DeserializeObject<MessageType>(message);
//            Debug.Log($"message type: {messageType.type}");
            switch (messageType.type) {
                case Messages.CONNECT:
                    handler.HandleConnect();
                    break;

                case Messages.START:
                    var startMessage = JsonConvert.DeserializeObject<StartMessage>(message);
                    handler.HandleStart(startMessage.players, startMessage.options);
                    break;

                case Messages.ACTION:
                    var actionMessage = JsonConvert.DeserializeObject<ActionMessage>(message);
                    handler.HandleActions(actionMessage.actions);
                    break;

                default:
                    Debug.LogWarning($"Communication: Unknown message type: {messageType.type}.");
                    break;
            }
        }

        /// <summary>
        /// Sends the game's manifest to the Training Module.
        /// </summary>
        /// <param name="name">name of the game</param>
        /// <param name="description">textual description of the game</param>
        /// <param name="possiblePlayers">a list containing a possible number of players that can simultaneously interact with the game</param>
        /// <param name="actionsDefinition">a definition of the actions (as a value class - see EZCoach.Value namespace)</param>
        /// <param name="statesDefinition">a definition of the state observations (as a value class - see EZCoach.Value namespace)</param>
        /// <param name="metricsNames">a list containing names of the metrics that the game will send along the state observations</param>
        public void SendManifest(string name, string description, int[] possiblePlayers, object actionsDefinition, object statesDefinition,
            string[] metricsNames) {
            var manifestMessage = new ManifestMessage() {
                name = name,
                description = description,
                players = possiblePlayers,
                actions = actionsDefinition,
                states = statesDefinition,
                metrics_names = metricsNames
            };
            var manifestJson = JsonConvert.SerializeObject(manifestMessage);
            if (debugMessages) {
                Debug.Log($"Sending message: {manifestJson}");
            }

            try {
                connection.Send(manifestJson);

            } catch (NotConnectedException) {
                connection.Restart();
            }
        }

        /// <summary>
        /// Sends the state observations, accumulated rewards, the running flags and metrics to the Training Module. Each element of state observations, accumulated rewards and running flags corresponds to each playing agent.
        /// </summary>
        /// <param name="states">a list of state observations (as defined in the manifest) for each player</param>
        /// <param name="accumulatedRewards">a list of accumulated rewards for each player</param>
        /// <param name="running">a list of flags indicating if the game is running for each player</param>
        /// <param name="metrics">a list of metrics corresponding the the list of metrics declared in the game's manifest</param>
        public void SendStates(IList states, List<float> accumulatedRewards, List<bool> running, float[] metrics) {
            var stateMessage = new StateMessage() {
                states = states,
                acc_rewards = accumulatedRewards,
                running = running,
                metrics = metrics
            };
            var stateMessageJson = JsonConvert.SerializeObject(stateMessage);
            if (debugMessages) {
                Debug.Log($"Sending message: {stateMessageJson}");
            }

            try {
                connection.Send(stateMessageJson);

            } catch (NotConnectedException) {
                handler.HandleStop();
                connection.Restart();
            }
        }

        /// <summary>
        /// An enum representing the method used for parsing messages.
        /// </summary>
        [Serializable]
        public enum UpdateMethod {
            LateUpdate,
            FixedUpdate
        }

        /// <summary>
        /// A class used for identifying message types received from the Training Module. The messages are identified by the type field.
        /// </summary>
        public class MessageType {
            public string type;
        }

        /// <summary>
        /// A class representing a start message received from the Training Module. It contains the selected number of players and options.
        /// </summary>
        [Serializable]
        private class StartMessage {
            public int players;
            public Dictionary<string, object> options;
        }

        /// <summary>
        /// A class representing an action message received from the Training Module. It contains a list of actions selected by the agents.
        /// </summary>
        private class ActionMessage {
            //{"type": "action", "actions": [0]}
            public object[] actions;
        }

        /// <summary>
        /// A class representing a state message which is sent to the Training Module.
        /// </summary>
        [Serializable]
        private class StateMessage {
            public readonly string type = "state";
            public IList states;
            public List<float> acc_rewards;
            public List<bool> running;
            public float[] metrics;
        }

        /// <summary>
        /// A class representing a manifest message which is sent to the Training Module.
        /// </summary>
        [Serializable]
        private class ManifestMessage {
            public readonly string type = "manifest";
            public string name;
            public string description;
            public int[] players;
            public object actions;
            public object states;
            public string[] metrics_names;
        }

        /// <summary>
        /// A class containing string representations of types of messages received from the Training Module.
        /// </summary>
        public static class Messages {
            public const string CONNECT = "connect";
            public const string START = "start";
            public const string ACTION = "action";
        }
    }
}