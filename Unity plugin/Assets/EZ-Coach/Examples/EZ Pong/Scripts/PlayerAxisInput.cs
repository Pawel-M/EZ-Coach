using UnityEngine;

namespace EZCoach.Pong {
    [RequireComponent(typeof(Player))]
    public class PlayerAxisInput : MonoBehaviour {

        [SerializeField] private string axis;

        private Player player;

        void Start() {
            player = GetComponent<Player>();
        }
        void Update() {
            if (!enabled || player == null)
                return;

            if (!Game.Round.Running) {
                player.InputDirection = PlayerDirection.None;
                return;
            }

            PlayerDirection direction = PlayerDirection.None;
            var axisValue = Input.GetAxis(axis);

            if (axisValue > 0) {
                direction = PlayerDirection.Up;

            } else if (axisValue < 0) {
                direction = PlayerDirection.Down;
            }

            player.InputDirection = direction;
        }
    }
}