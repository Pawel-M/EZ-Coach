using UnityEngine;

namespace EZCoach.Pong {
    [RequireComponent(typeof(Player))]
    public class PlayerExternalInput : MonoBehaviour {

        [Range(0f, .5f)]
        [SerializeField] private float deadZone;

        [SerializeField] private bool updateFromDeadZone = false;

        private Player player;

        void Start() {
            player = GetComponent<Player>();
        }
        
        public void ExternalInput(float input) {
            if (!enabled || player == null)
                return;
            
            PlayerDirection direction = PlayerDirection.None; 
            if (input > 0.5 + deadZone) {
                direction = PlayerDirection.Up;

            } else if (input < 0.5 - deadZone) {
                direction = PlayerDirection.Down;

            } else if (updateFromDeadZone) {
                direction = PlayerDirection.None;
            }

            player.InputDirection = direction;
        }
    }
}