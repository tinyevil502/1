using UnityEngine;

public class Enemy : MonoBehaviour
{
    [Header("敌人设置")]
    [SerializeField] private float maxHealth = 50f;
    [SerializeField] private float moveSpeed = 3f;
    [SerializeField] private bool showHealthBar = true;
    
    [Header("AI设置")]
    [SerializeField] private Transform target;
    [SerializeField] private float detectionRange = 10f;
    [SerializeField] private bool autoFindPlayer = true;
    
    private Health health;
    private BuffManager buffManager;
    private Renderer enemyRenderer;
    private Color originalColor;
    
    private void Awake()
    {
        // 确保敌人有必要的组件
        SetupComponents();
    }
    
    private void Start()
    {
        // 自动寻找玩家
        if (autoFindPlayer && target == null)
        {
            GameObject player = GameObject.FindGameObjectWithTag("Player");
            if (player != null)
            {
                target = player.transform;
            }
        }
        
        // 保存原始颜色
        enemyRenderer = GetComponent<Renderer>();
        if (enemyRenderer != null)
        {
            originalColor = enemyRenderer.material.color;
        }
        
        // 订阅健康事件
        if (health != null)
        {
            health.OnDeath += OnDeath;
            health.OnDamageTaken += OnDamageTaken;
        }
    }
    
    private void Update()
    {
        // 简单的AI移动
        if (target != null && health.IsAlive)
        {
            MoveTowardsTarget();
        }
        
        // 显示健康信息（仅调试用）
        if (showHealthBar && health != null)
        {
            DisplayHealthInfo();
        }
    }
    
    private void SetupComponents()
    {
        // 设置标签
        if (!gameObject.CompareTag("Enemy"))
        {
            gameObject.tag = "Enemy";
        }
        
        // 添加Health组件
        health = GetComponent<Health>();
        if (health == null)
        {
            health = gameObject.AddComponent<Health>();
        }
        health.SetMaxHealth(maxHealth);
        
        // 添加BuffManager组件
        buffManager = GetComponent<BuffManager>();
        if (buffManager == null)
        {
            buffManager = gameObject.AddComponent<BuffManager>();
        }
        
        // 确保有碰撞器
        Collider collider = GetComponent<Collider>();
        if (collider == null)
        {
            collider = gameObject.AddComponent<BoxCollider>();
        }
        
        // 确保有渲染器（如果没有则创建简单的立方体）
        if (GetComponent<Renderer>() == null)
        {
            // 创建一个简单的敌人外观
            GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Cube);
            visual.transform.SetParent(transform);
            visual.transform.localPosition = Vector3.zero;
            visual.transform.localScale = Vector3.one;
            visual.GetComponent<Renderer>().material.color = Color.red;
            
            // 移除多余的碰撞器
            Destroy(visual.GetComponent<Collider>());
        }
    }
    
    private void MoveTowardsTarget()
    {
        if (target == null) return;
        
        float distanceToTarget = Vector3.Distance(transform.position, target.position);
        
        // 如果在检测范围内，移动向目标
        if (distanceToTarget <= detectionRange)
        {
            Vector3 direction = (target.position - transform.position).normalized;
            transform.position += direction * moveSpeed * Time.deltaTime;
            
            // 面向目标
            transform.LookAt(target.position);
        }
    }
    
    private void DisplayHealthInfo()
    {
        // 简单的血量显示（在Scene视图中可见）
        Debug.DrawLine(
            transform.position + Vector3.up * 2f,
            transform.position + Vector3.up * 2f + Vector3.right * (health.HealthPercentage * 2f),
            Color.green
        );
        
        Debug.DrawLine(
            transform.position + Vector3.up * 2f + Vector3.right * (health.HealthPercentage * 2f),
            transform.position + Vector3.up * 2f + Vector3.right * 2f,
            Color.red
        );
    }
    
    private void OnDeath()
    {
        Debug.Log($"敌人 {gameObject.name} 死亡了！");
        
        // 播放死亡效果
        PlayDeathEffect();
        
        // 可以在这里添加掉落物品、经验值等逻辑
    }
    
    private void OnDamageTaken(float damage)
    {
        Debug.Log($"敌人 {gameObject.name} 受到 {damage} 点伤害");
        
        // 播放受伤效果
        PlayHurtEffect();
    }
    
    private void PlayDeathEffect()
    {
        // 简单的死亡效果：创建爆炸粒子或改变颜色
        if (enemyRenderer != null)
        {
            enemyRenderer.material.color = Color.black;
        }
    }
    
    private void PlayHurtEffect()
    {
        // 简单的受伤效果：短暂闪红
        if (enemyRenderer != null)
        {
            StartCoroutine(FlashColor(Color.red, 0.2f));
        }
    }
    
    private System.Collections.IEnumerator FlashColor(Color flashColor, float duration)
    {
        if (enemyRenderer != null)
        {
            Color original = enemyRenderer.material.color;
            enemyRenderer.material.color = flashColor;
            yield return new WaitForSeconds(duration);
            enemyRenderer.material.color = original;
        }
    }
    
    // 用于调试的方法
    [ContextMenu("测试受伤")]
    public void TestTakeDamage()
    {
        if (health != null)
        {
            health.TakeDamage(10f);
        }
    }
    
    [ContextMenu("应用中毒效果")]
    public void TestApplyPoison()
    {
        if (buffManager != null)
        {
            PoisonBuff poison = new PoisonBuff(1f, 0.2f, 5f);
            buffManager.AddBuff(poison);
        }
    }
    
    private void OnDrawGizmosSelected()
    {
        // 在Scene视图中显示检测范围
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, detectionRange);
    }
}