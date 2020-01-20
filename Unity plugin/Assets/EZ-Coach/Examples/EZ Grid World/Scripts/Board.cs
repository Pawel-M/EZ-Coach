using System;
using System.Collections.Generic;
using UnityEngine;

namespace EZCoach.GridWorld {
    public class Board {
        private IntVector2 size;
        private IntVector2 startingPosition;
        private IntVector2[] endPoints;
        private PositionReward[] rewards;
        private float defaultActionReward;
        private int maxMoves;
        private float maxMovesReward;

        private bool running = false;
        private int numMoves;
        private IntVector2 playerPosition;

        public Board(IntVector2 size, IntVector2 startingPosition, IntVector2[] endPoints, 
            PositionReward[] rewards, float defaultActionReward, int maxMoves, float maxMovesReward) {
            this.size = size;
            this.startingPosition = startingPosition;
            this.endPoints = endPoints;
            this.rewards = rewards;
            this.defaultActionReward = defaultActionReward;
            this.maxMoves = maxMoves;
            this.maxMovesReward = maxMovesReward;
        }

        public void Start() {
            playerPosition = startingPosition;
            numMoves = 0;
            running = true;
        }

        public List<MoveDirection> GetAllActions() {
            List<MoveDirection> actions = new List<MoveDirection>(5);
            if (size.x > 1) {
                actions.Add(MoveDirection.Left);
                actions.Add(MoveDirection.Right);
            }

            if (size.y > 1) {
                actions.Add(MoveDirection.Up);
                actions.Add(MoveDirection.Down);
            }

            return actions;
        }

        public List<MoveDirection> GetStateActions() {
            if (!running) {
                return null;
            }
            
            List<MoveDirection> actions = new List<MoveDirection>(5);
            
            if (playerPosition.x > 0) {
                actions.Add(MoveDirection.Left);
            }

            if (playerPosition.x < size.x - 1) {
                actions.Add(MoveDirection.Right);
            }
            
            if (playerPosition.y > 0) {
                actions.Add(MoveDirection.Down);
            }

            if (playerPosition.y < size.y - 1) {
                actions.Add(MoveDirection.Up);
            }

            return actions;
        }

        public float Move(MoveDirection direction) {
            if (!running)
                throw new GameEndedException();
            
            var reward = 0f;
            
            var possibleAction = GetStateActions();
            if (!possibleAction.Contains(direction)) {
                var oldAction = direction;
                direction = MoveDirection.None;
                reward += defaultActionReward;
                Debug.LogWarning($"Selected action ({oldAction}) is impossible in current state (player position {playerPosition})" +
                                 $"Making default action {direction} instead.");
            }

            if (direction == MoveDirection.None) {
//                playerPosition = playerPosition;

            }else if (direction == MoveDirection.Up) {
                playerPosition = playerPosition.AddY(1);
                    
            } else if (direction == MoveDirection.Down) {
                playerPosition = playerPosition.AddY(-1);
                
            } else if (direction == MoveDirection.Left) {
                playerPosition = playerPosition.AddX(-1);
                    
            } else { //direction == MoveDirection.Right
                playerPosition = playerPosition.AddX(1);
            }

            foreach (var positionReward in rewards) {
                if (positionReward.position != playerPosition)
                    continue;
                
                reward += positionReward.reward;
                break;
            }

            foreach (var endPoint in endPoints) {
                if (playerPosition != endPoint)
                    continue;
                
                running = false;
                break;
            }

            numMoves++;
            if (maxMoves > 0 && numMoves >= maxMoves) {
                reward += maxMovesReward;
                running = false;
            }
            
            return reward;
        }

        public int[,] GetState() {
            var state = new int[size.x, size.y];
            for (var x = 0; x < size.x; x++) {
                for (var y = 0; y < size.y; y++) {
                    state[x, y] = Cell.EMPTY;
                }
            }

            state[playerPosition.x, playerPosition.y] = Cell.PLAYER;
            foreach (var endPoint in endPoints) {
                state[endPoint.x, endPoint.y] = Cell.END;
            }
            
            return state;
        }

        public bool Running => running;

        public IntVector2 Size => size;

        public class GameEndedException : Exception { }
    }
}