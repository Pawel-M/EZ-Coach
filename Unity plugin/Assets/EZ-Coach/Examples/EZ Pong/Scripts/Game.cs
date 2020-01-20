using UnityEngine;

namespace EZCoach.Pong {
    public class Game : MonoBehaviour {

        [Range(0.1f, 100f)]
        [SerializeField] private float timeScale;

        [Range(0.1f, 100f)]
        [SerializeField] private float ballSpeed;
        [Range(0.1f, 100f)]
        [SerializeField] private float playersSpeed;

        [SerializeField] private float playerDeadBounceZone;
        [SerializeField] private float playerBounceChange;

        void Awake() {
            Time.timeScale = timeScale;
            
            Round = FindObjectOfType<Round>();
            TimeScale = timeScale;
            PlayerSpeed = playersSpeed;
            BallSpeed = ballSpeed;
            PlayerDeadBounceZone = playerDeadBounceZone;
            PlayerBounceChange = playerBounceChange;
        }

        public static Round Round {
            get;
            private set;
        }

        public static float TimeScale {
            get;
            private set;
        }
        
        public static float BallSpeed { 
            get; 
            private set;
        }

        public static float PlayerSpeed {
            get; 
            private set;
        }

        public static float PlayerDeadBounceZone {
            get;
            private set;
        }

        public static float PlayerBounceChange { 
            get; 
            private set; }
    }
}
