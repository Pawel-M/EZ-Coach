using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;

namespace EZCoach {
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

        private void UpdateInternal() {
            var message = connection.ObtainMessage();
            if (message != null) {
                ParseMessage(message);
            }
        }

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
                    var startMessage = JsonConvert.DeserializeObject<StartMessage<Dictionary<string, object>>>(message);
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

        // TODO: change actionsDefinition and statesDefinition to base value class
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

        [Serializable]
        public enum UpdateMethod {
            LateUpdate,
            FixedUpdate
        }

        public class MessageType {
            public string type;
        }

        [Serializable]
        private class StartMessage<T> {
            public int players;
            public T options;
        }

        private class ActionMessage {
            //{"type": "action", "actions": [0]}
            public object[] actions;
        }

        [Serializable]
        private class StateMessage {
            public readonly string type = "state";
            public IList states;
            public List<float> acc_rewards;
            public List<bool> running;
            public float[] metrics;
        }

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

        public static class Messages {
            public const string CONNECT = "connect";
            public const string START = "start";
            public const string ACTION = "action";
        }
    }
}