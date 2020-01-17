using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace EZCoach {
    /// <summary>
    /// A convenience abstract class that can be subclassed to easily integrate the communication of EZ-Coach. It needs Communication class to be initialized in the inspector.
    /// Use sendStatesMode to select when state observations should be sent. If Manual is selected, SendStates method must be invoked manually to send state observations.
    /// SkipTime can be used to send states with a specified delay (in seconds).
    /// Name, description and metricsNames are used to compose the game's manifest. 
    /// </summary>
    public abstract class CommunicationHandler : MonoBehaviour, ICommunicationHandler {
        [SerializeField] protected Communication communication;
        [SerializeField] protected SendStatesMode sendStatesMode;
        [SerializeField] protected float skipTime;
        [Header("Game")]
        [SerializeField] protected new string name;
        [TextArea]
        [SerializeField] protected string description;
        [SerializeField] protected string[] metricsNames;
        
        protected float nextSendTime = 0f;
        protected bool lastStateSent = true;
        protected float[] metrics;
        private bool internalRunning;
        private bool connected = false;
        
        protected virtual void Start() {
            communication.handler = this;
            
            metrics = new float[metricsNames.Length];
            for (int i = 0; i < metrics.Length; i++) {
                metrics[i] = 0f;
            }
        }

        protected virtual void FixedUpdate() {
            if (sendStatesMode == SendStatesMode.FixedUpdate) {
                InternalUpdate();
            }
        }

        protected virtual void LateUpdate() {
            if (sendStatesMode == SendStatesMode.LateUpdate) {
                InternalUpdate();
            }
        }

        /// <summary>
        /// Internal update method invoked by FixedUpdate or LateUpdate if corresponding sendStatesMode field was selected.
        /// </summary>
        protected virtual void InternalUpdate() {
            if (!CheckTime())
                return;

            internalRunning = CheckRunning();
            if (!internalRunning && lastStateSent)
                return;
            
            SendStates();
            lastStateSent = !internalRunning;
        }

        /// <summary>
        /// Checks if the state observations should be sent or to be delayed. Uses skipTime field to determine the delay.
        /// </summary>
        /// <returns></returns>
        protected virtual bool CheckTime() {
            if (skipTime <= 0f)
                return true;
            
            if (Time.time < nextSendTime)
                return false;
            
            nextSendTime = Time.time + skipTime;
            return true;
        }

        /// <summary>
        /// Sends state observations to the Training Module.
        /// Do not invoke this method if FixedUpdate or LateUpdate was selected as the sendStatesMode. If Manual was selected, use this method to select states at appropriate times.
        /// </summary>
        protected virtual void SendStates() {
            if (!connected)
                return;
            
            UpdateMetrics();
            communication.SendStates(GetStates(), GetAccumulatedRewards(), GetRunning(), metrics);
        }


        ///<inheritdoc cref="ICommunicationHandler.HandleStart"/>
        public abstract void HandleStart(int numPlayers, Dictionary<string, object> options = null);
        ///<inheritdoc cref="ICommunicationHandler.HandleActions"/>
        public abstract void HandleActions(object[] actions);
        ///<inheritdoc cref="ICommunicationHandler.HandleStop"/>
        public abstract void HandleStop();
        
        /// <summary>
        /// Returns if the game is running.
        /// </summary>
        /// <returns>true if the game is running, false otherwise</returns>
        protected abstract bool CheckRunning();
        
        /// <summary>
        /// Returns the list of state observations for each player. State observations must be compliant with the type defined in the game's manifest.
        /// </summary>
        /// <returns>a list of state observations for each player</returns>
        protected abstract IList GetStates();
        
        /// <summary>
        /// Returns the list of rewards accumulated by each player.
        /// </summary>
        /// <returns>a list of accumulated rewards for each player</returns>
        protected abstract List<float> GetAccumulatedRewards();
        
        /// <summary>
        /// Returns the running flag for each player. True means that the current episode has not ended yet for the corresponding player.
        /// </summary>
        /// <returns>a list of booleans indicating if the episode is running</returns>
        protected abstract List<bool> GetRunning();
        
        /// <summary>
        /// Returns a list of the possible players that can interact with the game simultaneously.
        /// </summary>
        /// <returns>a list of the possible number of players</returns>
        protected abstract int[] GetPossiblePlayers();
        
        /// <summary>
        /// The value object defining the accepted actions (see EZ-Coach.Value namespace for possible values).
        /// </summary>
        /// <returns>the object defining accepted actions (see EZ-Coach.Value namespace for possible values)</returns>
        protected abstract object GetActionsDefinition();
        
        /// <summary>
        /// The value object defining the state observations (see EZ-Coach.Value namespace for possible values).
        /// </summary>
        /// <returns>the object defining state observations (see EZ-Coach.Value namespace for possible values)</returns>
        protected abstract object GetStatesDefinition();
        protected abstract void UpdateMetrics();

        /// <summary>
        /// Handles the connect message by sending the game's manifest to the Training Module.
        /// </summary>
        public void HandleConnect() {
            var possiblePlayers = GetPossiblePlayers();
            var actionsDefinition = GetActionsDefinition();
            var statesDefinition = GetStatesDefinition();
            communication.SendManifest(name, description, possiblePlayers, actionsDefinition, statesDefinition, metricsNames);
            connected = true;
        }

        /// <summary>
        /// Enumeration representing three possible options for sending states: LateUpdate, FixedUpdate or Manual.
        /// </summary>
        [Serializable]
        protected enum SendStatesMode {
            LateUpdate, FixedUpdate, Manual
        }
    }
}