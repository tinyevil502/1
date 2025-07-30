using UnityEngine;

public class Bullet : MonoBehaviour
{
    [Header("子弹设置")]
    [SerializeField] private float speed = 10f;
    [SerializeField] private float damage = 5f;
    [SerializeField] private float lifetime = 5f;
    
    [Header("负面状态设置")]
    [SerializeField] private bool applyPoisonOnHit = true;
    [SerializeField] private float poisonDamage = 1f;
    [SerializeField] private float poisonInterval = 0.2f;
    [SerializeField] private float poisonDuration = 5f;
    
    [Header("目标设置")]
    [SerializeField] private LayerMask enemyLayerMask = -1;
    [SerializeField] private string enemyTag = "Enemy";
    
    private Rigidbody rb;
    private bool hasHit = false;
    
    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
        if (rb == null)
        {
            rb = gameObject.AddComponent<Rigidbody>();
            rb.useGravity = false;
        }
    }
    
    private void Start()
    {
        // 设置子弹移动方向
        rb.velocity = transform.forward * speed;
        
        // 设置生命周期
        Destroy(gameObject, lifetime);
    }
    
    private void OnTriggerEnter(Collider other)
    {
        if (hasHit) return;
        
        // 检查是否击中敌人
        if (IsEnemy(other.gameObject))
        {
            HitEnemy(other.gameObject);
        }
        else if (!other.isTrigger) // 击中其他物体（非触发器）
        {
            HitObstacle();
        }
    }
    
    private bool IsEnemy(GameObject target)
    {
        // 检查层级
        if ((enemyLayerMask & (1 << target.layer)) == 0)
            return false;
        
        // 检查标签
        if (!string.IsNullOrEmpty(enemyTag) && !target.CompareTag(enemyTag))
            return false;
        
        // 检查是否有Health组件
        return target.GetComponent<Health>() != null;
    }
    
    private void HitEnemy(GameObject enemy)
    {
        hasHit = true;
        
        Debug.Log($"子弹击中敌人: {enemy.name}");
        
        // 造成直接伤害
        Health enemyHealth = enemy.GetComponent<Health>();
        if (enemyHealth != null)
        {
            enemyHealth.TakeDamage(damage);
        }
        
        // 应用中毒效果
        if (applyPoisonOnHit)
        {
            ApplyPoisonBuff(enemy);
        }
        
        // 播放击中效果
        PlayHitEffect(enemy);
        
        // 销毁子弹
        DestroyBullet();
    }
    
    private void ApplyPoisonBuff(GameObject enemy)
    {
        BuffManager buffManager = enemy.GetComponent<BuffManager>();
        if (buffManager == null)
        {
            buffManager = enemy.AddComponent<BuffManager>();
        }
        
        // 创建中毒buff
        PoisonBuff poisonBuff = new PoisonBuff(poisonDamage, poisonInterval, poisonDuration);
        
        // 应用buff
        buffManager.AddBuff(poisonBuff);
        
        Debug.Log($"对 {enemy.name} 应用中毒效果：每 {poisonInterval} 秒造成 {poisonDamage} 点伤害，持续 {poisonDuration} 秒");
    }
    
    private void HitObstacle()
    {
        hasHit = true;
        Debug.Log("子弹击中障碍物");
        
        // 播放击中障碍物的效果
        PlayHitEffect(null);
        
        // 销毁子弹
        DestroyBullet();
    }
    
    private void PlayHitEffect(GameObject target)
    {
        // 这里可以添加击中特效
        // 例如粒子效果、声音效果等
        
        // 简单示例：创建一个临时的特效对象
        GameObject hitEffect = new GameObject("HitEffect");
        hitEffect.transform.position = transform.position;
        
        // 可以在这里添加粒子系统或其他视觉效果
        
        // 自动销毁特效
        Destroy(hitEffect, 1f);
    }
    
    private void DestroyBullet()
    {
        // 停止移动
        if (rb != null)
        {
            rb.velocity = Vector3.zero;
        }
        
        // 销毁子弹
        Destroy(gameObject);
    }
    
    // 公共方法用于设置子弹属性
    public void SetDamage(float newDamage)
    {
        damage = newDamage;
    }
    
    public void SetSpeed(float newSpeed)
    {
        speed = newSpeed;
        if (rb != null)
        {
            rb.velocity = transform.forward * speed;
        }
    }
    
    public void SetPoisonSettings(float poisonDmg, float interval, float duration)
    {
        poisonDamage = poisonDmg;
        poisonInterval = interval;
        poisonDuration = duration;
    }
    
    public void SetApplyPoison(bool apply)
    {
        applyPoisonOnHit = apply;
    }
}