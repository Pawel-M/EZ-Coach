using UnityEngine;

namespace EZCoach.Pong {
    [RequireComponent(typeof(Player))]
    public class PlayerFollowerInput : MonoBehaviour {

        [SerializeField] private float allowedDeltaPosition = 0;

        private Player player;

        void Start() {
            player = GetComponent<Player>();
        }
        void Update() {
            if (!enabled || player == null)
                return;

            PlayerDirection direction = PlayerDirection.None;
            
            if (player.Position.y > Game.Round.Ball.Position.y + allowedDeltaPosition) {
                direction = PlayerDirection.Down;

            } else if (player.Position.y < Game.Round.Ball.Position.y - allowedDeltaPosition) {
                direction = PlayerDirection.Up;

            } else {
                direction = PlayerDirection.None;
            }

            player.InputDirection = direction;
        }
    }
}