using System;
using System.Collections;
using System.Collections.Generic;
using EZCoach.Value;
using UnityEngine;

namespace EZCoach.Pong {
    public class PongHandler : CommunicationHandler {
        [Header("First Player")] 
        [SerializeField] private Player firstPlayer;
        [SerializeField] private PlayerAxisInput firstPlayerAxisInput;
        [SerializeField] private PlayerFollowerInput firstPlayerFollowerInput;
        [SerializeField] private PlayerExternalInput firstPlayerExternalInput;

        [Header("Second Player")] 
        [SerializeField] private Player secondPlayer;
        [SerializeField] private PlayerAxisInput secondPlayerAxisInput;
        [SerializeField] private PlayerFollowerInput secondPlayerFollowerInput;
        [SerializeField] private PlayerExternalInput secondPlayerExternalInput;
        [SerializeField] private AStateProvider stateProvider;

        [SerializeField] private bool userAsSecondPlayer;

        private Round round;
        private int numPlayers;
        private bool running = false;
        private List<float> accumulatedRewards;
        private List<bool> runnings;

        protected override void Start() {
            base.Start();
            round = FindObjectOfType<Round>();

            metrics = new float[metricsNames.Length];
            for (int i = 0; i < metrics.Length; i++) {
                metrics[i] = 0f;
            }
        }

        public override void HandleStop() {
            round.StopRound();
        }

        protected override bool CheckRunning() {
            return round.Running;
        }

        protected override IList GetStates() {
            return stateProvider.GetStates(numPlayers);
        }

        protected override List<float> GetAccumulatedRewards() {
            accumulatedRewards[0] = round.LeftPlayerPoints - round.RightPlayerPoints;

            if (numPlayers > 1) {
                accumulatedRewards[1] = round.RightPlayerPoints - round.LeftPlayerPoints;
            }
            return accumulatedRewards;
        }

        protected override List<bool> GetRunning() {
            runnings[0] = round.Running;
            if (numPlayers > 1) {
                runnings[1] = round.Running;
            }
            return runnings;
        }

        protected override int[] GetPossiblePlayers() {
            return new[] {1, 2};
        }

        protected override object GetActionsDefinition() {
            return new IntValue(new IntRange(-1, 1), "Move: up (-1), stay (0), down (1)");
        }

        protected override object GetStatesDefinition() {
            return stateProvider.GetStatesDefinition();
        }

        protected override void UpdateMetrics() {
            metrics[0] = firstPlayer.NumBounces; // bounces_1
            metrics[1] = secondPlayer.NumBounces; // bounces_2
        }


        public override void HandleStart(int numPlayers, Dictionary<string, object> options = null) {
            this.numPlayers = numPlayers;
            accumulatedRewards = new List<float>(numPlayers);
            runnings = new List<bool>(numPlayers);
            for (int i = 0; i < numPlayers; i++) {
                accumulatedRewards.Add(0f);
                runnings.Add(false);
            }

            firstPlayerExternalInput.enabled = true;
            firstPlayerAxisInput.enabled = false;
            firstPlayerFollowerInput.enabled = false;

            if (numPlayers == 2) {
                secondPlayerExternalInput.enabled = true;
                secondPlayerAxisInput.enabled = false;
                secondPlayerFollowerInput.enabled = false;

            } else {
                secondPlayerExternalInput.enabled = false;
                if (userAsSecondPlayer) {
                    secondPlayerAxisInput.enabled = true;
                    secondPlayerFollowerInput.enabled = false;
                } else {
                    secondPlayerFollowerInput.enabled = true;
                    secondPlayerAxisInput.enabled = false;
                }
            }

            round.ResetGame();
            round.StartRound();
            running = true;
        }

        public override void HandleActions(object[] actions) {
            int[] intActions = new int[actions.Length];
            for (int i = 0; i < actions.Length; i++) {
                intActions[i] = Convert.ToInt32(actions[i]);
            }

            var firstPlayerInput = intActions[0] == 0 ? 0.5f : intActions[0] == 1 ? 1f : 0f;
            firstPlayerExternalInput.ExternalInput(firstPlayerInput);

            if (numPlayers == 2) {
                var secondPlayerInput = intActions[1] == 0 ? 0.5f : intActions[1] == 1 ? 1f : 0f;
                secondPlayerExternalInput.ExternalInput(secondPlayerInput);
            }
        }
    }


}