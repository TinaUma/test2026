# Unity C# Developer — Planning Reference

## Principles
1. **ScriptableObjects for data** — spirits, enemies, waves, recipes = SO
2. **Composition over inheritance** — components, not deep hierarchies
3. **Object pooling** — no Instantiate/Destroy at runtime for frequent objects
4. **Events and delegates** — loose coupling between systems
5. **[SerializeField] private** — not public fields, encapsulation
6. **Async/await** — for loading, not coroutines where possible
7. **Addressables** — for assets, not Resources.Load

## Code Patterns

### Component Structure
```csharp
public class SpiritController : MonoBehaviour
{
    [Header("Data")]
    [SerializeField] private SpiritData _data;

    [Header("Runtime")]
    [SerializeField] private float _currentHealth;

    // Events
    public event Action<float> OnHealthChanged;
    public event Action OnDeath;

    // Cached references
    private Rigidbody2D _rb;
    private SpriteRenderer _sprite;

    private void Awake()
    {
        _rb = GetComponent<Rigidbody2D>();
        _sprite = GetComponent<SpriteRenderer>();
    }
}
```

### ScriptableObject Definition
```csharp
[CreateAssetMenu(fileName = "Spirit", menuName = "Taiga/Spirit")]
public class SpiritData : ScriptableObject
{
    [Header("Identity")]
    public string spiritName;
    public Sprite icon;
    public SpiritRole role;

    [Header("Stats")]
    public float baseHealth = 100f;
    public float baseDamage = 10f;
    public float moveSpeed = 5f;

    [Header("Evolution")]
    public EvolutionPath[] cozyPath;
    public EvolutionPath[] horrorPath;
}
```

### Object Pool Pattern
```csharp
public class ProjectilePool : MonoBehaviour
{
    [SerializeField] private GameObject _prefab;
    [SerializeField] private int _initialSize = 20;

    private Queue<GameObject> _pool = new();

    private void Awake()
    {
        for (int i = 0; i < _initialSize; i++)
        {
            var obj = Instantiate(_prefab, transform);
            obj.SetActive(false);
            _pool.Enqueue(obj);
        }
    }

    public GameObject Get()
    {
        var obj = _pool.Count > 0 ? _pool.Dequeue() : Instantiate(_prefab, transform);
        obj.SetActive(true);
        return obj;
    }

    public void Return(GameObject obj)
    {
        obj.SetActive(false);
        _pool.Enqueue(obj);
    }
}
```
