using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace EZCoach {
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

        protected virtual void InternalUpdate() {
            if (!CheckTime())
                return;

            internalRunning = CheckRunning();
            if (!internalRunning && lastStateSent)
                return;
            
            SendStates();
            lastStateSent = !internalRunning;
        }

        protected virtual bool CheckTime() {
            if (skipTime <= 0f)
                return true;
            
            if (Time.time < nextSendTime)
                return false;
            
            nextSendTime = Time.time + skipTime;
            return true;
        }

        protected virtual void SendStates() {
            if (!connected)
                return;
            
            UpdateMetrics();
            communication.SendStates(GetStates(), GetAccumulatedRewards(), GetRunning(), metrics);
        }


        public abstract void HandleStart(int numPlayers, Dictionary<string, object> options = null);
        public abstract void HandleActions(object[] actions);
        public abstract void HandleStop();
        protected abstract bool CheckRunning();
        protected abstract IList GetStates();
        protected abstract List<float> GetAccumulatedRewards();
        protected abstract List<bool> GetRunning();
        protected abstract int[] GetPossiblePlayers();
        protected abstract object GetActionsDefinition();
        protected abstract object GetStatesDefinition();
        protected abstract void UpdateMetrics();


        #region ICommunicationHandler methods        

        public void HandleConnect() {
            var possiblePlayers = GetPossiblePlayers();
            var actionsDefinition = GetActionsDefinition();
            var statesDefinition = GetStatesDefinition();
            communication.SendManifest(name, description, possiblePlayers, actionsDefinition, statesDefinition, metricsNames);
            connected = true;
        }

        #endregion

        [Serializable]
        protected enum SendStatesMode {
            LateUpdate, FixedUpdate, Manual
        }
    }
}