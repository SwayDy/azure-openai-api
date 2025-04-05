import os
import requests

API_URL = "http://localhost:8000/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.getenv('API_KEY')}"
}
data = {
    "model": "deepseek-r1",
    "messages": [{"role": "user", "content": "你是谁？"}],
    "stream": True,
}

def test_streaming_response():
    """测试流式响应功能"""
    with requests.post(API_URL, headers=headers, json=data, stream=True) as response:
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        chunks = []
        for line in response.iter_lines():
            if line:
                chunk = line.decode('utf-8')
                chunks.append(chunk)
                assert 'data: {"id":' in chunk, "Invalid response format"
        
        assert len(chunks) > 0, "No data received in streaming response"

def test_error_handling():
    """测试错误处理机制"""
    invalid_data = data.copy()
    invalid_data["messages"] = []
    
    response = requests.post(API_URL, headers=headers, json=invalid_data)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert "validation_error" in response.json()["error"]["type"], "Invalid error type"

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])
