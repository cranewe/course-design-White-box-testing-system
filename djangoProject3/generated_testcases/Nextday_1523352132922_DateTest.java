// LLM生成 - 测试用例 1
import static org.junit.jupiter.api.Assertions.*;
import java.time.LocalDate;
import org.junit.jupiter.api.Test;

class DateTest {

    @Test
    public void testIncrementNormalCase() throws Exception {
        // Arrange: 创建初始日期对象
        Date date = new Date(1, 31, 2023);

        // Act: 执行增量操作并获取结果
        date.increment();

        // Assert: 验证是否正确增加到下一天
        assertEquals("2/1/2023", date.toString());
    }
}

// LLM生成 - 测试用例 2
import static org.junit.jupiter.api.Assertions.*;
import java.time.LocalDate;
import org.junit.jupiter.api.Test;

class DateTest {

    @Test
    public void testCrossNewYearBoundary() throws Exception {
        // Arrange: 设置年末最后一天作为起始值
        Date date = new Date(12, 31, 2023);

        // Act: 增加一次后检查新年的第一天
        date.increment();

        // Assert: 确保成功进入新年第一日
        assertEquals("1/1/2024", date.toString());
    }
}

