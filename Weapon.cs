using UnityEngine;

public class Weapon : MonoBehaviour
{
    [Header("武器设置")]
    [SerializeField] private GameObject bulletPrefab;
    [SerializeField] private Transform firePoint;
    [SerializeField] private float fireRate = 1f; // 每秒发射次数
    [SerializeField] private float bulletSpeed = 15f;
    [SerializeField] private float bulletDamage = 5f;
    
    [Header("中毒子弹设置")]
    [SerializeField] private bool usePoisonBullets = true;
    [SerializeField] private float poisonDamage = 1f;
    [SerializeField] private float poisonInterval = 0.2f;
    [SerializeField] private float poisonDuration = 5f;
    
    [Header("输入设置")]
    [SerializeField] private KeyCode fireKey = KeyCode.Space;
    [SerializeField] private bool autoFire = false;
    
    private float nextFireTime = 0f;
    
    private void Update()
    {
        HandleInput();
    }
    
    private void HandleInput()
    {
        bool shouldFire = false;
        
        if (autoFire)
        {
            shouldFire = true;
        }
        else
        {
            shouldFire = Input.GetKey(fireKey);
        }
        
        if (shouldFire && CanFire())
        {
            Fire();
        }
    }
    
    private bool CanFire()
    {
        return Time.time >= nextFireTime;
    }
    
    public void Fire()
    {
        if (!CanFire()) return;
        
        // 更新下次可以开火的时间
        nextFireTime = Time.time + (1f / fireRate);
        
        // 创建子弹
        CreateBullet();
        
        Debug.Log("武器开火！");
    }
    
    private void CreateBullet()
    {
        GameObject bullet;
        
        if (bulletPrefab != null)
        {
            // 使用预制件创建子弹
            bullet = Instantiate(bulletPrefab, GetFirePosition(), GetFireRotation());
        }
        else
        {
            // 创建简单的子弹对象
            bullet = CreateSimpleBullet();
        }
        
        // 配置子弹
        ConfigureBullet(bullet);
    }
    
    private GameObject CreateSimpleBullet()
    {
        // 创建一个简单的子弹对象
        GameObject bullet = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        bullet.name = "Bullet";
        bullet.transform.localScale = Vector3.one * 0.1f;
        bullet.transform.position = GetFirePosition();
        bullet.transform.rotation = GetFireRotation();
        
        // 添加碰撞器并设置为触发器
        Collider collider = bullet.GetComponent<Collider>();
        if (collider != null)
        {
            collider.isTrigger = true;
        }
        
        // 添加子弹脚本
        bullet.AddComponent<Bullet>();
        
        return bullet;
    }
    
    private void ConfigureBullet(GameObject bullet)
    {
        Bullet bulletScript = bullet.GetComponent<Bullet>();
        if (bulletScript != null)
        {
            bulletScript.SetSpeed(bulletSpeed);
            bulletScript.SetDamage(bulletDamage);
            bulletScript.SetApplyPoison(usePoisonBullets);
            bulletScript.SetPoisonSettings(poisonDamage, poisonInterval, poisonDuration);
        }
    }
    
    private Vector3 GetFirePosition()
    {
        if (firePoint != null)
        {
            return firePoint.position;
        }
        return transform.position + transform.forward * 0.5f;
    }
    
    private Quaternion GetFireRotation()
    {
        if (firePoint != null)
        {
            return firePoint.rotation;
        }
        return transform.rotation;
    }
    
    // 公共方法用于外部调用
    public void SetFireRate(float newFireRate)
    {
        fireRate = Mathf.Max(0.1f, newFireRate);
    }
    
    public void SetBulletDamage(float newDamage)
    {
        bulletDamage = newDamage;
    }
    
    public void SetPoisonEnabled(bool enabled)
    {
        usePoisonBullets = enabled;
    }
    
    public void SetPoisonSettings(float damage, float interval, float duration)
    {
        poisonDamage = damage;
        poisonInterval = interval;
        poisonDuration = duration;
    }
    
    // 用于调试的方法
    [ContextMenu("测试开火")]
    public void TestFire()
    {
        Fire();
    }
}