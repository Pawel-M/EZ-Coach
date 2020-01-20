using System;
using System.Collections.Generic;
using EZCoach.Value;
using UnityEngine;

namespace EZCoach.Pong {
    public class VectorStateProvider : AStateProvider {
        private Round round;

        private void Start() {
            round = FindObjectOfType<Round>();
        }

        public override object GetStatesDefinition() {
                        var ranges = new[] {
                new FloatRange(-20f, 20f), // player position y 
                new FloatRange(-34.5f, 34.5f), // ball position x
                new FloatRange(-21f, 21f), // ball position y
                new FloatRange(-40f, 40f), // ball velocity y
                new FloatRange(-40f, 40f), // ball velocity y
                new FloatRange(-19f, 19f), // opponent position y 
            };
            var description = "Vector of values, automatically flipped so that the current player is on the left):\n" +
                              "[player position y, ball position x and y, ball velocity x and y, opponent position y]";
            return new FloatList(ranges, description);
        }

        public override List<object> GetStates(int numPlayers) {
            if (numPlayers > round.Players.Length)
                throw new ArgumentException($"Argument numPlayers ({numPlayers}) must not be greater than number of current players.");
            
            var states = new List<object>(numPlayers);
            for (int i = 0; i < numPlayers; i++) {
                var isFirstPlayer = i % 2 == 0;
                var gameIndex = Mathf.FloorToInt(i / 2f);
                var opponentIndex = gameIndex + (isFirstPlayer ? 1 : 0);
                var player = round.Players[i];
                var opponent = round.Players[opponentIndex];
                var state = new [] {
                    player.Position.y, 
                    round.Ball.Position.x * (isFirstPlayer ? 1f : -1f), 
                    round.Ball.Position.y, 
                    round.Ball.Velocity.x * (isFirstPlayer ? 1f : -1f), 
                    round.Ball.Velocity.y,
                    opponent.Position.y
                };
                states.Add(state);
            }
            return states;
        }
    }
}