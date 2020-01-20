using UnityEngine;

namespace EZCoach.Pong {
    public class KillWall : MonoBehaviour {
        [SerializeField] private PlayerNumber winningPlayer;
        private void OnCollisionEnter2D(Collision2D other) {
            Game.Round.PlayerWon(winningPlayer);
        }
    }
}