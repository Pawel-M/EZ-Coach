using System;
using System.Collections;
using System.Collections.Generic;
using EZCoach.Value;
using UnityEngine;

namespace EZCoach.GridWorld {
    public class ExternalCommunicator : CommunicationHandler {
        [SerializeField] private BoardsManager board;

        private float accumulatedReward = 0f;
        private List<MoveDirection> possibleActions;

        protected override void Start() {
            base.Start();
            possibleActions = board.GetAllActions();
        }

        protected override int[] GetPossiblePlayers() {
            return new[] {1};
        }

        protected override object GetActionsDefinition() {
            var actions = new List<int>(possibleActions.Count);
            foreach (var possibleAction in possibleActions) {
                actions.Add((int) possibleAction);
            }

            var actionsDescription = "move action";
            for (int i = 0; i < possibleActions.Count; i++) {
                var action = possibleActions[i];
                actionsDescription += $", {i}:{action.ToString()}";
            }
            
            return new IntValue(new IntRange(0, actions.Count - 1), actionsDescription);
        }

        protected override object GetStatesDefinition() {
            var size = board.Size.x * board.Size.y;
            var range = new IntRange(Cell.EMPTY, Cell.END);
            var description = $"flattened cells of size {board.Size.x}x{board.Size.y}: " +
                              $"wall:{Cell.WALL}, " +
                              $"empty:{Cell.EMPTY}, " +
                              $"player:{Cell.PLAYER}, " +
                              $"end:{Cell.END}";
            var definition = new IntList(size, range, description: description);
            return definition;
        }

        public override void HandleStart(int numPlayers, Dictionary<string, object> options = null) {
            board.Reset();
            accumulatedReward = 0;
            SendStates();
        }

        public override void HandleActions(object[] actions) {
            var action = actions[0];
            var reward = board.Move(possibleActions[Convert.ToInt32(action)]);
            accumulatedReward += reward;

            SendStates();
        }

        public override void HandleStop() {
            board.Reset();
        }

        protected override bool CheckRunning() {
            return board.Running;
        }

        protected override IList GetStates() {
            var states = new List<object>();
            var state = board.GetState();
            var flattenState = new int[state.Length];
            var i = 0;
            foreach (var v in state) {
                flattenState[i] = v;
                i++;
            }
            states.Add(flattenState);
            return states;
        }

        protected override List<float> GetAccumulatedRewards() {
            var accumulatedRewards =  new List<float>();
            accumulatedRewards.Add(accumulatedReward);
            return accumulatedRewards;
        }

        protected override List<bool> GetRunning() {
            var accumulatedRewards =  new List<bool>();
            accumulatedRewards.Add(board.Running);
            return accumulatedRewards;
        }

        protected override void UpdateMetrics() {
            
        }
    }
}